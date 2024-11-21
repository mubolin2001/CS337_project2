
from bs4 import BeautifulSoup
import requests
from recipe import *
import spacy
import re
from answering import *
def fetch_recipe(url):
    """Fetch the recipe from the given URL and parse it."""
    # check if the URL is a valid AllRecipes.com URL
    if "allrecipes.com" in url:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = soup.find('h1').text.strip() if soup.find('h1') else "Unknown Recipe"
            #load models
            nlp = spacy.load("en_core_web_md")
            # SIMILARITY_THEREHOLD = 0.9
            
            # Extract ingredients
            ingredients_section = soup.find_all('ul', {'class': 'mm-recipes-structured-ingredients__list'})
            ingredient_items = soup.find_all('li', class_='mm-recipes-structured-ingredients__list-item')
            ingredient_list = []
            for item in ingredient_items:
                
                quantity = item.find('span', {'data-ingredient-quantity': 'true'}).text.strip() if item.find('span', {'data-ingredient-quantity': 'true'}) else ""
                unit = item.find('span', {'data-ingredient-unit': 'true'}).text.strip() if item.find('span', {'data-ingredient-unit': 'true'}) else ""
                name = item.find('span', {'data-ingredient-name': 'true'}).text.strip() if item.find('span', {'data-ingredient-name': 'true'}) else ""
                ingredient = Ingredient(name,quantity, unit)
                ingredient_list.append(ingredient)

            # Extract steps
            steps_section = soup.find_all('li', {'class': 'comp mntl-sc-block mntl-sc-block-startgroup mntl-sc-block-group--LI'})
            # print(steps_section)
            # steps = [step.text.strip() for step in steps_section]
            steps = []
            for step_str in steps_section:
                step = Step(step_str.text.strip(), None, None)
                steps.append(step)
                # found_ingredients = []
                # for ingredient in ingredient_list:
                #     ingredient_doc = nlp(ingredient.name)
                #     for token in doc:
                #         token_doc = nlp(token.text)
                #         similarity = ingredient_doc.similarity(token_doc)
                #         if similarity >= SIMILARITY_THEREHOLD:
                #             found_ingredients.append((token, ingredient))
                #             break
                # found_ingredients = list(set(found_ingredients))
                # step.founding_list = found_ingredients
            # recipe = Recipe(ingredient, None, None, steps)
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
            current_step = 0
            return (ingredient_list, None, None, steps, current_step, title )
        else:
            return {"error": f"Failed to fetch the recipe. HTTP Status Code: {response.status_code}"}
    else:
        print("please enter a valid url")

def get_intent(input):
    user_input = input.split(" ")
    if "next" in user_input:
        return ("go_next", 0)
    if "back" in user_input or "previous" in user_input:
        return ("go_previous", 0)
    if "repeat" in user_input:
        return ("repeat", 0)
    pattern = r"\b(\d+)(st|nd|rd|th)\b"
    step_match = re.search(pattern, input, re.IGNORECASE)
    if step_match:
        step_num = step_match.group(1)
        return ("jumping", int(step_num))
    if "ingredient" in user_input and "list" in user_input:
        return ("show_ingredient_list", 0)
    return ("unknown", 0)

def handle_other_questions(user_input):
    if is_what_is_question(user_input):
        print("Bot:", handle_what_is_question(user_input))
    elif is_how_to_question(user_input):
        print("Bot:", handle_how_to_question(user_input))
    elif is_vague_how_to_question(user_input):
        print("Bot:", handle_vague_how_to_question(user_input))
    else:
        print("Bot: I am not sure what you are asking. Please ask me a valid question.")

def main():
    """Main bot interaction for fetching and displaying a recipe."""
    print("Bot: Hi there! Please provide a recipe URL from AllRecipes.com.")

    while True:
        url = input("User: ").strip()

        if not url.startswith("http"):
            url = f"https://{url}"
        print("Bot: Sure, let me fetch the recipe for you...")

        ingredient_list, tool, method, steps, current_step, title  = fetch_recipe(url)


        print(f"Bot: Alright! I fetched the recipe titled: \"{title}\".")
        print("Bot: What do you want to do next?")
        print("Options:\n1. Show ingredients\n2. Show steps\n3. Exit")
            
        while True:
            user_input = input("User: ").strip()
            if user_input == "1":
                print("Bot: Here are the ingredients:")
                for ingredient in ingredient_list:
                    print(ingredient.quantity, ingredient.measurement, ingredient.name)
                print("Bot: What do you want to do next?")
                print("Options:\n1. Show ingredients\n2. Show steps\n3. Exit")
            elif user_input == "2":

                print(f"Bot: Here are the step {current_step + 1}")
                print(steps[current_step].text)
                print("ask me any questions or go next.")
                while True:
                    user_input = input("User: ").strip()
                    intent, step_num = get_intent(user_input)
                    # go next 
                    if intent == "go_next":
                        if current_step < len(steps) - 1:
                            current_step += 1
                            print(f"Bot: Here are the step {current_step + 1}")
                            print(steps[current_step].text)
                            print("ask me any questions")
                        else:
                            print("This is the last step")
                    # go back
                    if intent == "go_previous":
                        if current_step > 0:
                            current_step -= 1
                            print(f"Bot: Here are the step {current_step + 1}")
                            print(steps[current_step].text)
                            print("ask me any questions")
                        else:
                            print("This is the first step")
                    #repeat
                    if intent == "repeat":
                        print(f"Bot: Here are the step {current_step + 1}")
                        print(steps[current_step].text)
                        print("ask me any questions")
                    #jumping
                    if intent == "jumping":
                        if step_num > 0 and step_num <= len(steps):
                            current_step = step_num -1
                            print(f"Bot: Here are the step {current_step + 1}")
                            print(steps[current_step].text)
                            print("ask me any questions")
                        else:
                            print(f"There are only {len(steps)} steps.")

                    #show ingredient list
                    if intent == "show_ingredient_list":
                        print("Bot: Here are the ingredients:")
                        for ingredient in ingredient_list:
                            print(ingredient.quantity, ingredient.measurement, ingredient.name)
                            print("ask me any questions")

                    if intent == "unknown":
                        handle_other_questions(user_input)
                                    
            elif user_input.lower() in ["3", "exit"]:
                print("Bot: Goodbye!")
                return
            else:
                print("Bot: Please choose a valid option (1, 2, or 3).")


# Run the bot interaction
if __name__ == "__main__":
    main()
