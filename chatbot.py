from bs4 import BeautifulSoup
import requests
import spacy
import re
import spacy
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from rapidfuzz.distance.Postfix_py import similarity
from torch.fx.experimental.unify_refinements import substitute_solution_one_type

from recipe import *


class RecipeBot:
    def __init__(self):
        self.recipe_title = None
        self.ingredients = []
        self.steps = []
        self.current_step = 0
        self.nlp = spacy.load("en_core_web_md")
        self.similarity_threshold = 0.9
        self.conversation_history = open("conversation_history.txt", "w")
        self.conversation_history.write("")

    def fetch_recipe(self, url):
        """
        Fetch the recipe from the given URL and parse it.
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract title
            self.recipe_title = soup.find('h1').text.strip() if soup.find('h1') else "Unknown Recipe"

            # Extract ingredients
            ingredient_items = soup.find_all('li', class_='mm-recipes-structured-ingredients__list-item')
            self.ingredients = []
            for item in ingredient_items:
                quantity = item.find('span', {'data-ingredient-quantity': 'true'}).text.strip() if item.find('span', {
                    'data-ingredient-quantity': 'true'}) else ""
                unit = item.find('span', {'data-ingredient-unit': 'true'}).text.strip() if item.find('span', {
                    'data-ingredient-unit': 'true'}) else ""
                name = item.find('span', {'data-ingredient-name': 'true'}).text.strip() if item.find('span', {
                    'data-ingredient-name': 'true'}) else ""
                self.ingredients.append(Ingredient(name, quantity, unit))

            # Extract steps
            steps_section = soup.find_all('li', {
                'class': 'comp mntl-sc-block mntl-sc-block-startgroup mntl-sc-block-group--LI'})
            self.steps = [Step(step.text.strip(), None, None) for step in steps_section]

            # Link steps for navigation
            for i in range(len(self.steps)):
                if i > 0:
                    self.steps[i].previous = self.steps[i - 1]
                if i < len(self.steps) - 1:
                    self.steps[i].next = self.steps[i + 1]

        else:
            raise Exception(f"Failed to fetch the recipe. HTTP Status Code: {response.status_code}")

    def get_intent(self, input):
        """
        Determine the intent of the user's query.
        """
        user_input = input.lower()
        quant_query = self.detect_quantity(user_input)

        if "ingredient" in user_input:
            return ("show_ingredient_list", 0)
        elif "step" in user_input or "procedure" in user_input:
            return ("show_step", 0)

        if self.detect_vague_question(user_input):
            return ("vague_question", 0)
        if self.detect_external_question(user_input):
            return ("external_question", 0)
        if self.detect_temp(user_input):
            return ("temp", self.current_step)
        if self.detect_time(user_input):
            return ("time", self.current_step)
        if self.detect_substitute(user_input):
            return ("substitute", 0)
        if quant_query:
            return ("ingredient_quantity", quant_query)

        return ("unknown", 0)

    def single_respond(self, intent, aux, query):
        """
        Respond to a single query. No internal continuous loop required.
        :param query:
        :return:
        """
        if intent == "unknown":
            print("Bot: I'm sorry, I didn't understand that.")
            return

        if intent == "show_ingredient_list":
            print("Bot: Here are the ingredients:")
            for ing in self.ingredients:
                print(f"- {ing.quantity} {ing.measurement} {ing.name}")

        if intent == "ingredient_quantity":
            ingredient = aux
            flag = False
            if ingredient is None:
                print("Didn't find the ingredient. Any typo?")
                return
            for ing in self.ingredients:
                for i in ingredient:
                    similarity = self.nlp(ing.name).similarity(self.nlp(i))
                    if similarity >= self.similarity_threshold:
                        flag = True
                        print(f"You need {ing.quantity} {ing.measurement} of {ing.name}.")
                        self.conversation_history.write(f"You need {ing.quantity} {ing.measurement} of {ing.name}.\n")
                        continue
            if not flag:
                print("Ingredient not found in the recipe.")

        if intent == "external_question":
            self.handle_external_question(query)
        if intent == "vague_question":
            self.handle_vague_question()

        if intent == "temp":
            #print("Found the temperature.")
            self.handle_temp(self.steps[self.current_step].text)
        if intent == "time":
            #print("Found the time.")
            self.handle_time(self.steps[self.current_step].text)


    def respond(self, query):
        """
        Respond to the user's query based on intent.
        """
        intent, aux = self.get_intent(query)

        if intent == "show_step":
            while True:
                print(f"Bot: Here is step {self.current_step + 1}:")
                print(self.steps[self.current_step].text)
                self.conversation_history.write(self.steps[self.current_step].text + "\n")
                print("Ask me any questions or say 'next', 'back', 'repeat', or 'exit'.")
                question = input("User: ").strip()
                if "exit" in question.lower():
                    break
                sub_intent, sub_aux = self.get_intent(question.lower())
                #print(f"Sub-intent: {sub_intent}, Sub-aux: {sub_aux}")

                if 'next' in question.lower():
                    if self.current_step < len(self.steps) - 1:
                        self.current_step += 1
                    else:
                        print("This is the last step.")
                elif 'back' in question.lower() or 'previous' in question.lower() or 'last' in question.lower():
                    if self.current_step > 0:
                        self.current_step -= 1
                    else:
                        print("This is the first step.")
                elif 'repeat' in question.lower():
                    continue

                elif self.detect_jump_step(question) != -1:
                    if self.detect_jump_step(question) > len(self.steps):
                        print("Invalid step number.")
                    else:
                        self.current_step = self.detect_jump_step(question) - 1
                        continue
                else:
                    self.single_respond(sub_intent, sub_aux, question)

        else:
            self.single_respond(intent, aux, query)

        return "I'm sorry, I didn't understand that."

    # Detect all kinds of query types
    # Returns the detected information if necessary
    def detect_temp(self, query):
        """Detect the temperature in the current step."""
        match = re.search(r"what is the temperature|temperature", query, re.IGNORECASE)
        if match:
            return True # return the matched temperature
        return False

    def detect_time(self, query):
        """Detect the time in the current step."""
        match = re.search(r"how long|how much time|what is the amount of time|when", query, re.IGNORECASE)
        if match:
            return True
        return False

    def detect_quantity(self, query):
        """Detect the quantity of an ingredient in the query."""
        tokens = word_tokenize(query)
        filtered_tokens = [token for token in tokens if token.lower() not in stopwords.words("english")]
        new_query = " ".join(filtered_tokens)
        doc = self.nlp(new_query)
        # Extract nouns (potential ingredients)
        ingredients = [token.text for token in doc if token.pos_ in {"NOUN", "PROPN"}]
        return ingredients if ingredients else None

    def detect_jump_step(self, query):
        """Detect the step number to jump to in the query."""
        pattern = r"(?:jump to|go to|navigate to|move to)\s+step\s+(\d+)"
        match = re.search(pattern, query)
        if match:
            return int(match.group(1))
        return -1

    def detect_external_question(self, query):
        pattern = r"(?:how do I|what is a|what is an)"
        match = re.search(pattern, query)
        if match:
            return True
        return False

    def detect_vague_question(self, query):
        pattern = r"(?:how do I do this|how do I do that)"
        match = re.search(pattern, query)
        if match:
            return True
        return False

    def detect_exit(self, query):
        pattern = r"(?:exit|quit|stop)"
        match = re.search(pattern, query)
        if match:
            self.conversation_history.close()
            return True
        return False

    def detect_substitute(self, query):
        doc = self.nlp(query)
        substitutes = ['instead', 'substitute', 'replace', 'swap']
        for token in doc:
            if token.pos_ == "VERB" or token.pos_ == "ADV":
                similarity = 0
                for sub in substitutes:
                    similarity = max(self.nlp(token.text).similarity(self.nlp(sub)), similarity)
                if similarity >= self.similarity_threshold:
                    return True
        return False


    # Handle all kinds of query types
    # Prints the bot's response directly
    def handle_external_question(self, query, platform="google"):
        """Handle external questions by searching on Google or YouTube."""
        user_input = query.lower().replace(" ", "+")

        if platform == "google":
            search_url = f"https://www.google.com/search?q={user_input}"
        else:
            search_url = f"https://www.youtube.com/results?search_query={query}"

        self.conversation_history.write(f"Here is the search result for your question: {search_url}\n")
        print(f"Here is the search result for your question: {search_url}")

    def handle_vague_question(self):
        """Handle vague questions by seeking the latest chat history, and then
        ask it on google."""
        # Seek the answer from the conversation history
        try:
            lines = self.conversation_history.readlines()
            if lines:
                self.handle_external_question(lines[-1])
            else:
                return "I'm sorry, I don't have an answer to that."
        except Exception as e:
            print(f"Error: file not found.")
            return

    def handle_temp(self, query):
        """Handle temperature related questions."""
        match = re.search(r"(\d+)\s?(°C|°F|degrees F|degrees C|degrees)", query, re.IGNORECASE)
        if match:
            print(f"The temperature is {match.group(0)}")
        else:
            print("No temperature specified.")

    def handle_time(self, query):
        """Handle time related questions."""
        print("Looking for time...")
        match = re.search(r"(\d+)\s?(minutes|hours|seconds)", query, re.IGNORECASE)
        if match:
            print(f"The time is {match.group(0)}")
        else:
            print("No time specified.")

