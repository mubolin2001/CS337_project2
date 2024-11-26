# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []
import re
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import FollowupAction, SlotSet
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from recipe import *
import json

postfix = {1: "st", 2: "nd", 3: "rd"}

# reset memory
def reset():
    return [SlotSet("recipe_url", None), SlotSet("recipe_object", None), SlotSet("current_step_index", None)]

class ActionValidateURL(Action):
    def name(self) -> str:
        return "action_validate_url"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> list:
        user_message = tracker.latest_message.get("text")
        url_match = re.search(r'https?://(?:www\.)?allrecipes\.com/.*', user_message)

        if url_match:
            url = url_match.group(0)  # Extract the first matched URL
            dispatcher.utter_message(text=f"Got it! Let's start working with the recipe from that URL: {url}")
            return [SlotSet("recipe_url", url), FollowupAction("action_parse_recipe")]
        else:
            dispatcher.utter_message(text="The URL doesn't seem to be from AllRecipes.com. Please provide a valid recipe URL.")
            return [FollowupAction("utter_ask_url")]

        return []

class ActionParseRecipe(Action):
    def name(self) -> str:
        return "action_parse_recipe"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> list:
        # Get the URL provided by the user
        url = tracker.get_slot("recipe_url")

        if not url:
            dispatcher.utter_message(text="I didn't receive a valid URL. Please provide a recipe URL.")
            return []

        # Try to fetch the recipe data from the URL
        try:
            reset()
            dispatcher.utter_message(text=f"Sure, let me fetch the recipe from {url}")
            headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'lxml')

            # Parse the title
            title = soup.find('h1').text.strip() if soup.find('h1') else "Unknown Recipe"

            # Parse ingredients
            ingredients = self.parse_ingredients(soup)

            # Parse cooking methods
            cooking_methods = self.parse_methods(soup)

            # Parse steps
            steps = self.parse_steps(soup, ingredients)

            tools = []

            recipe = Recipe(title, ingredients, tools, cooking_methods, steps)

            dispatcher.utter_message(text=f"Alright. So let's start working with '{title}'. What do you want to do?")
            dispatcher.utter_message(text="[1] Go over ingredients list\n[2] Go over recipe steps.")

            return [
                SlotSet("recipe_object", json.dumps(recipe.to_dict())),
                SlotSet("user_context", "menu")
            ]

        except Exception as e:
            dispatcher.utter_message(text=f"Sorry, I couldn't fetch the recipe. Error: {e}")
            return []

    def parse_ingredients(self, soup):
        ingredients_section = soup.find_all('ul', {'class': 'mm-recipes-structured-ingredients__list'})
        ingredient_items = soup.find_all('li', class_='mm-recipes-structured-ingredients__list-item')
        ingredient_list = []
        for item in ingredient_items:
            quantity = item.find('span', {'data-ingredient-quantity': 'true'}).text.strip() if item.find('span', {'data-ingredient-quantity': 'true'}) else ""
            unit = item.find('span', {'data-ingredient-unit': 'true'}).text.strip() if item.find('span', {'data-ingredient-unit': 'true'}) else ""
            name = item.find('span', {'data-ingredient-name': 'true'}).text.strip() if item.find('span', {'data-ingredient-name': 'true'}) else ""
            ingredient = Ingredient(name,quantity, unit)
            ingredient_list.append(ingredient)
        
        return ingredient_list

    def parse_methods(self, soup):
        method_elements = soup.find_all('span', class_='cooking-method')
        primary_method = ""
        other_method = ""
        for idx, element in enumerate(method_elements):
            if idx == 0:
                primary_method = element.text.strip()
            else:
                other_method += element.text.strip() + " "
        methods = Method(primary_method, other_method)
        return methods

    def parse_steps(self, soup, ingredients):
        steps_section = soup.find_all('li', {'class': 'comp mntl-sc-block mntl-sc-block-startgroup mntl-sc-block-group--LI'})
        steps = []

        # nlp = spacy.load("en_core_web_md")
        similarity_threshold = 0.9

        for step_str in steps_section:
            step = Step(step_str.text.strip(), None, None)
            
            # find parameters for each step
            # ingredients
            ingredients_at_step = {}
            temperature_at_step = None
            time_at_step = None
            tool_substitution_at_step = None

            # find ingredients
            for ingredient in ingredients:
                ingredient_name = ingredient.name
                if ingredient_name in step.text:
                    ingredients_at_step[ingredient_name] = ingredient.quantity
            step.ingredients = ingredients_at_step

            # find temperature in the text
            temperature_pattern = re.compile(r"(\d+)\s*(?:degrees|°)?\s*(F|C)")
            temperature_element = re.search(temperature_pattern, step.text)
            if temperature_element:
                temperature_at_step = temperature_element.group(0)
            step.temperature = temperature_at_step

            # find time
            time_pattern = re.compile(r"\d+\s?min|\d+\s?hour")
            time_element = re.search(time_pattern, step.text)
            if time_element:
                time_at_step = time_element.group(0)
            step.time = time_at_step

            steps.append(step)
        
        return steps

class ActionShowIngredients(Action):
    def name(self) -> str:
        return "action_show_ingredients"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> list:
        if not tracker.get_slot("recipe_url"):
            dispatcher.utter_message(text="Please provide a recipe URL first.")
            return [FollowupAction("utter_ask_url")]
        
        recipe = tracker.get_slot("recipe_object")
        recipe = json.loads(recipe)

        user_input = tracker.latest_message.get("text")
        if user_input == "2":
            return [SlotSet("user_context", "steps"),
                    FollowupAction("action_take_to_first_step")]

        # Show the list of ingredients
        dispatcher.utter_message(text="Here are the ingredients:")
        for ingredient in recipe['ingredients']:
            dispatcher.utter_message(text=f"{ingredient['quantity']} {ingredient['measurement']} {ingredient['name']}")

        return []

class ActionTakeToFirstStep(Action):
    def name(self) -> str:
        return "action_take_to_first_step"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> list:
        if not tracker.get_slot("recipe_url"):
            dispatcher.utter_message(text="Please provide a recipe URL first.")
            return [FollowupAction("utter_ask_url")]
        user_input = tracker.latest_message.get("text")
        user_context = tracker.get_slot("user_context")
        if user_input == "1" and user_context == "menu":
            return [FollowupAction("action_show_ingredients")]
        SlotSet("user_context", "steps")
        # Set the step to the first one
        recipe = tracker.get_slot("recipe_object")
        recipe = json.loads(recipe)
        step = recipe['steps'][0]
        dispatcher.utter_message(text=f"Taking you to the first step: {step['text']}.")
        return [SlotSet("current_step_index", 0)]

class ActionShowNextStep(Action):
    def name(self) -> str:
        return "action_show_next_step"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> list:
        if not tracker.get_slot("recipe_url"):
            dispatcher.utter_message(text="Please provide a recipe URL first.")
            return [FollowupAction("utter_ask_url")]

        # load the current step index as integer
        if tracker.get_slot("current_step_index") is None:
            current_step_index = 0
        else:
            current_step_index = int(tracker.get_slot("current_step_index"))
        #dispatcher.utter_message(text=f"current step index: {current_step_index}")

        recipe = tracker.get_slot("recipe_object")
        recipe = json.loads(recipe)

        # Increment index and get the next step
        next_step_index = current_step_index + 1
        if next_step_index < len(recipe['steps']):
            dispatcher.utter_message(text=f"The {next_step_index + 1}"
                                     f"{postfix[next_step_index + 1] if next_step_index + 1 in postfix else 'th'} "
                                     f"step is: {recipe['steps'][next_step_index]['text']}"
                                     )
            return [SlotSet("current_step_index", next_step_index)]
        else:
            dispatcher.utter_message(text="You are already at the last step.")
            return []
        return []

class ActionShowPreviousStep(Action):
    def name(self) -> str:
        return "action_show_previous_step"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> list:
        if not tracker.get_slot("recipe_url"):
            dispatcher.utter_message(text="Please provide a recipe URL first.")
            return [FollowupAction("utter_ask_url")]

        current_step_index = int(tracker.get_slot("current_step_index")) or 0
        recipe = tracker.get_slot("recipe_object")
        recipe = json.loads(recipe)
        # Decrement index and get the previous step
        prev_step_index = current_step_index - 1
        if prev_step_index >= 0:
            dispatcher.utter_message(text=f"The {prev_step_index + 1}"
                                     f"{postfix[prev_step_index + 1] if prev_step_index + 1 in postfix else 'th'} "
                                     f"step is: {recipe['steps'][prev_step_index]['text']}"
                                     )
            return [SlotSet("current_step_index", prev_step_index)]
        else:
            dispatcher.utter_message(text="You are already at the first step.")
            return []

class ActionRepeatCurrentStep(Action):
    def name(self) -> str:
        return "action_repeat_current_step"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> list:
        if not tracker.get_slot("recipe_url"):
            dispatcher.utter_message(text="Please provide a recipe URL first.")
            return [FollowupAction("utter_ask_url")]

        current_step_index = int(tracker.get_slot("current_step_index")) or 0
        recipe = tracker.get_slot("recipe_object")
        recipe = json.loads(recipe)
        # Repeat the current step
        dispatcher.utter_message(text=f"The current step is: {recipe['steps'][current_step_index]['text']}")
        return []

class ActionTakeToNthStep(Action):
    def name(self) -> str:
        return "action_take_to_nth_step"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> list:
        if not tracker.get_slot("recipe_url"):
            dispatcher.utter_message(text="Please provide a recipe URL first.")
            return [FollowupAction("utter_ask_url")]

        step_number = list(tracker.get_latest_entity_values("step_number"))
        if not step_number:
            dispatcher.utter_message(text="I couldn't understand which step you want to go to.")
            return []

        recipe = tracker.get_slot("recipe_object")
        recipe = json.loads(recipe)

        step_number = self.convert_to_index(step_number[0])
        # Take user to the nth step (handling out-of-bounds errors)
        if step_number and 0 <= step_number - 1 < len(recipe['steps']):
            dispatcher.utter_message(text=f"The {step_number}"
                                     f"{postfix[step_number] if step_number in postfix else 'th'} "
                                     f"step is: {recipe['steps'][step_number - 1]['text']}"
                                     )
            return [SlotSet("current_step_index", step_number - 1)]
        else:
            dispatcher.utter_message(text="Invalid step number.")
            return []
    
    def convert_to_index(self, step_number):
        ordinals = {
            "first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5, "sixth": 6, 
            "seventh": 7, "eighth": 8, "ninth": 9, "tenth": 10
            }
        if step_number.isdigit():
            return int(step_number)
        return ordinals.get(step_number.lower(), None)

class ActionProvideStepDetails(Action):
    def name(self) -> str:
        return "action_provide_step_details"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> list:
        # Get the latest user message
        user_input = tracker.latest_message.get("text")
        current_step = tracker.get_slot("current_step_index")
        
        # Check if we have a current step
        if current_step is None:
            dispatcher.utter_message(text="I don't know which step you're referring to. Please start from the beginning or navigate to a step.")
            return []

        recipe = tracker.get_slot("recipe_object")
        recipe = json.loads(recipe)
        current_step_index = int(tracker.get_slot("current_step_index"))
        current_step = recipe['steps'][current_step_index]

        # Handle parameter-related questions about the current step
        if re.search(r"how much|quantity", user_input, re.IGNORECASE):
            return self.handle_quantity_query(dispatcher, current_step)
        elif re.search(r"temperature", user_input, re.IGNORECASE):
            return self.handle_temperature_query(dispatcher, current_step)
        elif re.search(r"how long|time", user_input, re.IGNORECASE):
            return self.handle_time_query(dispatcher, current_step)
        elif re.search(r"when is it done", user_input, re.IGNORECASE):
            return self.handle_done_query(dispatcher, current_step)
        elif re.search(r"substitute", user_input, re.IGNORECASE):
            return self.handle_substitution_query(dispatcher, current_step)
        else:
            dispatcher.utter_message(text="I didn't quite understand that. Could you rephrase or ask about the ingredients, temperature, time, or substitutions?")
            return []

    def handle_quantity_query(self, dispatcher: CollectingDispatcher, current_step) -> list:
        ingredients = current_step['ingredients']
        if ingredients:
            ingredient_list = "\n".join([f"{ingredient['name']}: {ingredient['quantity']} {ingredient['measurement']}" for ingredient in ingredients])
            dispatcher.utter_message(text=f"Here are the ingredients and their quantities:\n{ingredient_list}")
        else:
            dispatcher.utter_message(text="I couldn't find the ingredients for this step. Please check again.")
        return []

    def handle_temperature_query(self, dispatcher: CollectingDispatcher, current_step) -> list:
        # Example: Assume the step has a temperature instruction
        temperature = current_step['temperature']
        if temperature:
            dispatcher.utter_message(text=f"The required temperature is {temperature} degrees.")
        else:
            dispatcher.utter_message(text="Sorry, I couldn't find the temperature for this step.")
        return []

    def handle_time_query(self, dispatcher: CollectingDispatcher, current_step) -> list:
        # Example: Assume the step has a time instruction
        time = current_step['time']
        if time:
            dispatcher.utter_message(text=f"You should cook for {time}.")
        else:
            dispatcher.utter_message(text="Sorry, I couldn't find the cooking time for this step.")
        return []

    def handle_done_query(self, dispatcher: CollectingDispatcher, current_step) -> list:
        # Example: Assume the step has a done indication
        done_indicator = current_step.get("done_indicator", None)
        if done_indicator:
            dispatcher.utter_message(text=f"You'll know it's done when: {done_indicator}.")
        else:
            dispatcher.utter_message(text="Sorry, I couldn't find a done indicator for this step.")
        return []

    def handle_substitution_query(self, dispatcher: CollectingDispatcher, current_step) -> list:
        # Example: Assume current_step has a substitution option
        substitutions = current_step.get("substitutions", None)
        if substitutions:
            dispatcher.utter_message(text=f"You can substitute the following:\n{substitutions}")
        else:
            dispatcher.utter_message(text="Sorry, I couldn't find any substitutions for this step.")
        return []

class ActionAnswerQuestions(Action):
    def name(self) -> str:
        return "action_answer_questions"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        user_message = tracker.latest_message.get("text").lower()  # User's latest message
        current_step = tracker.get_slot("current_step")  # Current step in the recipe
        recipe = tracker.get_slot("recipe_object")  # Recipe object
        recipe = json.loads(recipe)

        # Handle "what is" questions
        if "what is" in user_message:
            return self.handle_what_is_question(user_message, dispatcher)

        # Handle "how to" questions (specific)
        elif "how to" in user_message:
            return self.handle_how_to_question(user_message, dispatcher)

        # Handle vague "how to" questions
        elif "how do i do that" in user_message or "how to do that" in user_message:
            current_step = recipe['steps'][int(tracker.get_slot("current_step_index"))]
            return self.handle_vague_how_to_question(dispatcher, current_step)

        # Fallback for unrecognized question types
        dispatcher.utter_message(text="Sorry, I couldn't understand your question. Could you please clarify?")
        return []

    def handle_what_is_question(self, user_message, dispatcher):
        # Example for simple tool-related questions

        tool = re.search(r"what is (?:an|a) (\w+)", user_message)
        if tool:
            tool_name = tool.group(1)
            google_url = f"https://www.google.com/search?q=what+is+a+{tool_name}"
            youtube_url = f"https://www.youtube.com/results?search_query=what+is+a+{tool_name}"
            dispatcher.utter_message(text=f"Here are some links to learn about {tool_name}:\n- Google: {google_url}\n- YouTube: {youtube_url}")
        else:
            dispatcher.utter_message(text="Sorry, I couldn't find any information on that tool.")
        return []

    def handle_how_to_question(self, user_message, dispatcher):
        # Handle specific "how to" questions (e.g., "How do I preheat the oven?")
        technique = re.search(r"how to (.+)", user_message)  # Extract the technique
        if technique:
            technique_name = technique.group(1)
            google_url = f"https://www.google.com/search?q=how+to+{technique_name}"
            youtube_url = f"https://www.youtube.com/results?search_query=how+to+{technique_name}"
            dispatcher.utter_message(text=f"Here are some links to learn how to {technique_name}:\n- Google: {google_url}\n- YouTube: {youtube_url}")
        else:
            dispatcher.utter_message(text="Sorry, I couldn't find instructions for that technique.")
        return []

    def handle_vague_how_to_question(self, dispatcher, current_step):
        # Handle vague "how to" questions like "How do I do that?"
        if current_step:
            # Assuming 'current_step' contains a description of what the user is working on (e.g., a technique)
            technique = current_step.get("text")  
            google_url = f"https://www.google.com/search?q=how+to+{technique.replace(' ', '+')}"
            youtube_url = f"https://www.youtube.com/results?search_query=how+to+{technique.replace(' ', '+')}"
            dispatcher.utter_message(text=f"Here are some links to learn how to {technique}:\n- Google: {google_url}\n- YouTube: {youtube_url}")
        else:
            dispatcher.utter_message(text="Sorry, I couldn't find any reference to what you're trying to do. Could you please clarify?")
        return []    