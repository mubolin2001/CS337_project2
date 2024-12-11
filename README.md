# Recipe Rasa
## Prerequisites
- We use python 3.10
- Run the following command to install the required packages
  - ```pip install -r requirements.txt```


## How to run
- Run the following command to start the chatbot
  - ```rasa train```
  - run ```rasa run actions``` in one console
  - run ```rasa shell``` in another
- Follow the instructions in the terminal to interact with the chatbot
- If you want to check ingredients for a recipe, say something like 'ingredients for <recipe_name>' in the terminal
- If you want to check the steps for a recipe, say something like 'steps for <recipe_name>' or 'show me the steps' in 
the terminal. As long as you include 'steps', the chatbot will do the job.
- While printing steps, you can ask params for the specific steps.
- If you are unsure about what the bot just said, ask a vague question or just say 'repeat'.
- Bot can handle external questions, it uses google by default. If you wish to see a video, just tell the bot!
- If you want to exit the chatbot, say something like 'exit' in the terminal

## tests
- <span style="color: green;">Bot loaded. Type a message and press enter (use '/stop' to exit):</span>
- Your input ->  yo
- <span style="color: blue;">Hello! How can I assist you today?</span>
- <span style="color: blue;">Please provide me with the URL of the recipe you'd like me to fetch.</span>
- Your input ->  Here's the link: https://www.allrecipes.com/recipe/218091/classic-and-simple-meat-lasagna/
- <span style="color: blue;">Got it! Let's start working with the recipe from that URL: https://www.allrecipes.com/recipe/218091/classic-and-simple-meat-lasagna/</span>
- <span style="color: blue;">Sure, let me fetch the recipe from https://www.allrecipes.com/recipe/218091/classic-and-simple-meat-lasagna/</span>
- <span style="color: blue;">Alright. So let's start working with 'Classic and Simple Meat Lasagna'. What do you want to do?</span>
- <span style="color: blue;">[1] Go over ingredients list</span>
- <span style="color: blue;">[2] Go over recipe steps.</span>
- Your input ->  1
- <span style="color: blue;">Here are the ingredients:</span>
- <span style="color: blue;">12  whole wheat lasagna noodles</span>
- <span style="color: blue;">1 pound lean ground beef</span>
- <span style="color: blue;">2 cloves garlic, chopped</span>
- <span style="color: blue;">1 teaspoon dried oregano, or to taste</span>
- <span style="color: blue;">½ teaspoon garlic powder</span>
- <span style="color: blue;">salt and ground black pepper to taste</span>
- <span style="color: blue;">1 (16 ounce) package cottage cheese</span>
- <span style="color: blue;">½ cup shredded Parmesan cheese</span>
- <span style="color: blue;">2  eggs</span>
- <span style="color: blue;">4 ½ cups tomato-basil pasta sauce</span>
- <span style="color: blue;">2 cups shredded mozzarella cheese</span>
- Your input ->  2
- <span style="color: blue;">Taking you to the first step: Preheat the oven to 350 degrees F (175 degrees C)..</span>
- Your input ->  What temperature should the oven be?
- <span style="color: blue;">The required temperature is 350 degrees F degrees.</span>
- Your input ->  next
- <span style="color: blue;">The 2nd step is: Bring a large pot of lightly salted water to a boil. Add lasagna noodles and cook for 10 minutes or until al dente; drain.</span>
- Your input ->  continue
- <span style="color: blue;">The 3rd step is: Meanwhile, place ground beef, garlic, oregano, garlic powder, salt, and black pepper in a large skillet over medium heat; cook and stir until beef is crumbly and evenly browned, about 10 minutes.</span>
- Your input ->  back
- <span style="color: blue;">The 2nd step is: Bring a large pot of lightly salted water to a boil. Add lasagna noodles and cook for 10 minutes or until al dente; drain.</span>
- Your input ->  step 5
- <span style="color: blue;">The 5th step is: Lay 4 noodles side by side on the bottom of a 9x13-inch baking pan; top with a layer of prepared tomato-basil sauce, a layer of ground beef mixture, and a layer of cottage cheese mixture. Repeat layers twice more, ending with a layer of sauce; sprinkle mozzarella cheese on top. Cover the dish with aluminum foil.</span>
- Your input ->  how to lay noodles
- <span style="color: blue;">Here are some links to learn how to lay:</span>
- <span style="color: blue;">- Google: https://www.google.com/search?q=how+to+lay</span>
- <span style="color: blue;">- YouTube: https://www.youtube.com/results?search_query=how+to+lay</span>
- Your input ->  step 1
- <span style="color: blue;">The 1st step is: Preheat the oven to 350 degrees F (175 degrees C).</span>
- Your input ->  how do i do that
- <span style="color: blue;">Here are some links to learn how to Preheat the oven to 350 degrees F (175 degrees C).:</span>
- <span style="color: blue;">- Google: https://www.google.com/search?q=how+to+Preheat+the+oven+to+350+degrees+F+(175+degrees+C).</span>
- <span style="color: blue;">- YouTube: https://www.youtube.com/results?search_query=how+to+Preheat+the+oven+to+350+degrees+F+(175+degrees+C).</span>
- Your input -> /stop
## for project3
- Your input -> https://www.allrecipes.com/recipe/16167/beef-bourguignon-i/    
- <span style = "color: yellow;">- Sure, let me fetch the recipe from https://www.allrecipes.com/recipe/16167/beef-bourguignon-i/
Alright. So let's start working with 'Beef Bourguignon'. What do you want to do?
[1] Go over ingredients list
[2] Go over recipe steps.
Your input ->  1                                                                                     
Here are the ingredients:
3 cups Burgundy wine
2  onions, thinly sliced
2  carrots, chopped
2 tablespoons brandy
1 clove garlic, crushed
10  whole black peppercorns
1 teaspoon salt
1 sprig fresh parsley
1  bay leaf
2 pounds cubed beef chuck roast
4 tablespoons olive oil, divided
¼ pound bacon, cubed
2  onions, chopped
3 tablespoons all-purpose flour
2 cloves garlic, crushed
1 tablespoon tomato paste
1 (10.5 ounce) can beef broth
salt and pepper to taste
4 tablespoons butter
1 pound fresh mushrooms, sliced </span>
- Your input ->  transform it to vegetarian 
- <span style = "color: yellow;"> The recipe has been transformed to vegetarian! </span>
Your input ->  1    
- <span style = "color: yellow;">Here are the ingredients:
3 cups Burgundy wine
2  onions, thinly sliced
2  carrots, chopped
2 tablespoons brandy
1 clove garlic, crushed
10  whole black peppercorns
1 teaspoon salt
1 sprig fresh parsley
1  bay leaf
2 pounds cubed <b style = "color: white">mushrooms</b> chuck roast
4 tablespoons olive oil, divided
¼ pound salted vegetables, cubed
2  onions, chopped
3 tablespoons all-purpose flour
2 cloves garlic, crushed
1 tablespoon tomato paste
1 (10.5 ounce) can mushrooms broth
salt and pepper to taste
4 tablespoons <b style = "color: white">vegetarian butter</b>
1 pound fresh mushrooms, sliced</span>
### We also have such transformation in the steps. Besides, feel free to try health, non-health, gluten-free, lactose-free recipe by typing "transform it to ... recipe.


