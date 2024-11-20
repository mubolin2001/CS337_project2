# Recipe chatbot
## Prerequisites
- We use python 3.10
- Run the following command to install the required packages
  - ```pip install -r requirements.txt```
  - ```python -m spacy download en_core_web_sm ```

## How to run
- Run the following command to start the chatbot
  - ```python main.py```
- Follow the instructions in the terminal to interact with the chatbot
- If you want to check ingredients for a recipe, say something like 'ingredients for <recipe_name>' in the terminal
- If you want to check the steps for a recipe, say something like 'steps for <recipe_name>' or 'show me the steps' in 
the terminal. As long as you include 'steps', the chatbot will do the job.
- While printing steps, you can ask params for the specific steps.
- If you are unsure about what the bot just said, ask a vague question or just say 'repeat'.
- Bot can handle external questions, it uses google by default. If you wish to see a video, just tell the bot!
- If you want to exit the chatbot, say something like 'exit' in the terminal
