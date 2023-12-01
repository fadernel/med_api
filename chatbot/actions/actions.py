# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

import requests
import json 

class Utils():
    @staticmethod
    def find_highest_value(data):
        max_key = max(data, key=data.get)
        max_value = data[max_key]
        return max_key, max_value

class ActionProccessImage(Action):
    
    API_ENDPOINT = 'http://localhost:8000/proccessimage'
    API_KEY = 'LambtonProject'

    def name(self) -> Text:
        return "action_process_image"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:


        headers = {'x-token': self.API_KEY}
        res = requests.get(url = self.API_ENDPOINT, headers=headers)
        if res.status_code != 404:
            response = json.loads(res.text)
            disease, value = Utils.find_highest_value(response)
            
            if disease.lower() != 'no finding':
                message=f"After an in-depth analysis, there is a high probability that the patient has {disease}"
            else:
                message=f"After an in-depth analysis, there is a high probability that the patient does not have any diseases"
        else:
                message=f"Please upload the image. Then type 'analyze'"

        dispatcher.utter_message(text=message)
        
        return []
    

