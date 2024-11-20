from chatbot import RecipeBot
import nltk

def main():
    bot = RecipeBot()
    print("Bot: Hi there! Please provide a recipe URL from AllRecipes.com.")

    while True:
        url = input("User: ").strip()
        if not url.startswith("http"):
            url = f"https://{url}"
        print("Bot: Sure, let me fetch the recipe for you...")

        try:
            bot.fetch_recipe(url)
        except Exception as e:
            print(f"Bot: {e}")
            continue

        print(f"Bot: Alright! I fetched the recipe titled: \"{bot.recipe_title}\".")
        print("Bot: What do you want to do next?")
        print("Options:\n1. Show ingredients\n2. Show steps\n3. Exit")

        while True:
            user_input = input("User: ").strip()
            if bot.detect_exit(user_input):
                print("Bot: Goodbye!")
                break
            bot.respond(user_input)


if __name__ == "__main__":
    nltk.download('punkt')
    nltk.download('stopwords')
    main()