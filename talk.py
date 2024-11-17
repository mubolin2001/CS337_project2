from bs4 import BeautifulSoup
import requests
from recipe import *
def fetch_recipe(url):
    """Fetch the recipe from the given URL and parse it."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = soup.find('h1').text.strip() if soup.find('h1') else "Unknown Recipe"
            
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
            # steps = [step.text.strip() for step in steps_section]
            steps = []
            for step_str in steps_section:
                step = Step(step_str.text.strip(), None, None)
                steps.append(step)
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

                    
                

            return {
                'title': title,
                'ingredients': ingredient_list,
                'steps': steps
            }
        else:
            return {"error": f"Failed to fetch the recipe. HTTP Status Code: {response.status_code}"}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}



def main():
    """Main bot interaction for fetching and displaying a recipe."""
    print("Bot: Hi there! Please provide a recipe URL from AllRecipes.com.")

    while True:
        url = input("User: ").strip()
        if not url.startswith("http"):
            url = f"https://{url}"
        print("Bot: Sure, let me fetch the recipe for you...")

        recipe_data = fetch_recipe(url)

        if 'error' in recipe_data:
            print(f"Bot: Oops! {recipe_data['error']}")
            print("Bot: Please try again with a valid URL.")
            print("current url: " + url)
        else:
            print(f"Bot: Alright! I fetched the recipe titled: \"{recipe_data['title']}\".")
            print("Bot: What do you want to do next?")
            print("Options:\n1. Show ingredients\n2. Show steps\n3. Exit")
            
            while True:
                user_input = input("User: ").strip()
                if user_input == "1":
                    print("Bot: Here are the ingredients:")
                    for ingredient in recipe_data['ingredients']:
                        print(f"- {ingredient}")
                elif user_input == "2":
                    print("Bot: Here are the steps:")
                    for i, step in enumerate(recipe_data['steps'], start=1):
                        print(f"Step {i}: {step}")
                elif user_input.lower() in ["3", "exit"]:
                    print("Bot: Goodbye!")
                    return
                else:
                    print("Bot: Please choose a valid option (1, 2, or 3).")

# Run the bot interaction
if __name__ == "__main__":
    main()
