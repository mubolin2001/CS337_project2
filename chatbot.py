import requests
from bs4 import BeautifulSoup
from parse import parse_recipe

def fetch_recipe(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        for tag in soup(["script", "style", "meta", "noscript"]):
            tag.decompose()
        raw_text = soup.get_text(separator='\n', strip=True)
        return raw_text
        # return parse_recipe(raw_text)
    except requests.RequestException as e:
        return {"error": f"Failed to fetch recipe: {e}"}


def chatbot():
    print("Hello! I am a recipe chatbot. I can help you find recipes and cooking instructions.")
    while True:
        user_input = input("Enter a recipe URL or type 'quit' to exit: ")
        if user_input.lower() == 'quit':
            print("Goodbye!")
            break
        else:
            recipe_data = fetch_recipe(user_input)
            if 'error' in recipe_data:
                print(recipe_data['error'])
            else:
                print_recipe(recipe_data)


