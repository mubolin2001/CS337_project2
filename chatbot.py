from bs4 import BeautifulSoup
import requests
import spacy
import re
import spacy
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


from recipe import *


class RecipeBot:
    def __init__(self):
        self.recipe_title = None
        self.ingredients = []
        self.steps = []
        self.current_step = 0
        self.nlp = spacy.load("en_core_web_md")
        self.similarity_threshold = 0.9

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

    def respond(self, query):
        """
        Respond to the user's query based on intent.
        """
        intent, aux = self.get_intent(query)

        if intent == "show_ingredient_list":
            print("Bot: Here are the ingredients:")
            for ing in self.ingredients:
                print(f"- {ing.quantity} {ing.measurement} {ing.name}")
        elif intent == "show_step":
            print(f"Bot: Here is step {self.current_step + 1}:")
            while True:
                print(self.steps[self.current_step].text)
                print("Ask me any questions or say 'next', 'back', 'repeat', or 'exit'.")
                question = input("User: ").strip()
                if 'next' in question.lower():
                    if self.current_step < len(self.steps) - 1:
                        self.current_step += 1
                    else:
                        print("This is the last step.")
                elif 'back' in question.lower() or 'previous' in question.lower():
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

                if "exit" in question.lower():
                    break

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
                        continue
            if not flag:
                print("Ingredient not found in the recipe.")

        return "I'm sorry, I didn't understand that."

    def get_intent(self, input):
        """
        Determine the intent of the user's query.
        """
        user_input = input.lower()
        quant_query = self.detect_quantity(user_input)

        if "ingredient" in user_input:
            return ("show_ingredient_list", 0)
        elif "step" in user_input:
            return ("show_step", 0)

        if quant_query:
            return ("ingredient_quantity", quant_query)

        return ("unknown", 0)

    def detect_quantity(self, query):
        tokens = word_tokenize(query)
        filtered_tokens = [token for token in tokens if token.lower() not in stopwords.words("english")]
        new_query = " ".join(filtered_tokens)
        doc = self.nlp(new_query)
        # Extract nouns (potential ingredients)
        ingredients = [token.text for token in doc if token.pos_ in {"NOUN", "PROPN"}]
        return ingredients if ingredients else None

    def detect_jump_step(self, query):
        pattern = r"(?:jump to|go to|navigate to|move to)\s+step\s+(\d+)"
        match = re.search(pattern, query)
        if match:
            return int(match.group(1))
        return -1

    def detect_exit(self, query):
        pattern = r"(?:exit|quit|stop)"
        match = re.search(pattern, query)
        if match:
            return True