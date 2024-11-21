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
from rasa_sdk.events import FollowupAction
from urllib.parse import urlparse
from recipe import *

class ActionValidateURL(Action):
    def name(self) -> str:
        return "action_validate_url"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> list:
        user_message = tracker.latest_message.get("text")
        url_match = re.search(r'https?://(?:www\.)?allrecipes\.com/.*', user_message)

        if url_match:
            url = url_match.group(0)  # Extract the first matched URL
            dispatcher.utter_message(text=f"Got it! Let's start working with the recipe from that URL: {url}")
        else:
            dispatcher.utter_message(text="The URL doesn't seem to be from AllRecipes.com. Please provide a valid recipe URL.")
            return [FollowupAction("utter_ask_url")]

        return []




