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
            steps = self.parse_steps(soup)

            # Format the parsed data and present it to the user
            message = f"Recipe: {title}\n\nIngredients:\n"
            for ingredient in ingredients:
                message += f"{ingredient.quantity}, {ingredient.measurement}, {ingredient.name}\n"

            message += "\nCooking Methods:\n" + "\n".join(cooking_methods) + "\n\nSteps:\n"
            for idx, step in enumerate(steps):
                message += f"Step {idx + 1}: {step.text}\n"

            dispatcher.utter_message(text=message)

        except Exception as e:
            dispatcher.utter_message(text=f"Sorry, I couldn't fetch the recipe. Error: {e}")
            return []

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
        methods = []
        method_elements = soup.find_all('span', class_='cooking-method')
        for method in method_elements:
            methods.append(method.text.strip())
        return methods

    def parse_steps(self, soup):
        steps_section = soup.find_all('li', {'class': 'comp mntl-sc-block mntl-sc-block-startgroup mntl-sc-block-group--LI'})
        steps = []
        for step_str in steps_section:
            step = Step(step_str.text.strip(), None, None)
            steps.append(step)
        for step_idx in range(len(steps)):
            if step_idx == 0:
                steps[step_idx].previous = None
                steps[step_idx].next = steps[step_idx + 1]
            elif step_idx != 0 and step_idx != len(steps) - 1:
                steps[step_idx].previous = steps[step_idx - 1]
                steps[step_idx].next = steps[step_idx + 1]
            elif step_idx == len(steps) - 1:
                steps[step_idx].previous = steps[step_idx - 1]
                steps[step_idx].next = None               
        return steps


