"""
Given an url of a recipe, parse the recipe and return the ingredients and instructions
"""
import requests
from bs4 import BeautifulSoup
from lxml.doctestcompare import strip


class Ingredient:

    def __init__(self):
        self.name = ''
        self.quantity = ''
        self.measurement = ''


class Recipe:

    def __init__(self):
        self.ingredients = []
        self.steps = []
        self.tools = []

    def add_ingredient(self, ingredient):
        self.ingredients.append(ingredient)


def parse_recipe(url):
    """
    Parse the recipe and return the ingredients and instructions
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')

        title_raw = soup.find('h1', class_='headline')
        title = title_raw.get_text(strip=True) if title_raw else 'No title Found'

        print('Title:', title)
        print(soup.get_text(strip=True))

        # Extract ingredients
        ingredients = []
        ingredient_elements = soup.select('.ingredients-item span.ingredients-item-name')
        for ingredient in ingredient_elements:
            ingredients.append(ingredient.get_text(strip=True))

        # Extract instructions
        instructions = []
        instruction_elements = soup.select('.instructions-section-item .paragraph')
        for instruction in instruction_elements:
            instructions.append(instruction.get_text(strip=True))

        # Return the parsed recipe data
        return {
            "title": title,
            "ingredients": ingredients,
            "instructions": instructions
        }

    except requests.RequestException as e:
        print(f"Error fetching the recipe: {e}")
        return None
    except Exception as e:
        print(f"Error parsing the recipe: {e}")
        return None



