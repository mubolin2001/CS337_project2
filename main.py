from chatbot import fetch_recipe
from parse import parse_recipe


res = fetch_recipe("https://www.allrecipes.com/recipe/218091/classic-and-simple-meat-lasagna/")
with open('recipe_output_new.txt', 'w') as f:
    f.write(res)