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
import os

#User disease
U_DISEASE = ''

class Utils():
    @staticmethod
    def find_highest_value(data):
        max_key = max(data, key=data.get)
        max_value = data[max_key]
        return max_key, max_value

class ActionProccessImage(Action):
    
    API_ENDPOINT = 'http://127.0.0.1:8000'+'/proccessimage'
    API_KEY = 'LambtonProject'


    def name(self) -> Text:
        return "action_process_image"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        username = tracker.get_slot('user_name')
        
        if username is not None:
        
            global U_DISEASE
            
            headers = {'x-token': self.API_KEY}
            res = requests.get(url = self.API_ENDPOINT, headers=headers)
            if res.status_code != 404:
                response = json.loads(res.text)
                disease, value = Utils.find_highest_value(response)
                U_DISEASE = disease
                
                if disease.lower() != 'no finding':
                    message=f"After an in-depth analysis, there is a high probability that the patient {username} has {disease}"
                else:
                    message=f"After an in-depth analysis, there is a high probability that the patient {username} does not have any diseases"
            else:
                    message=f"Please upload the image. Then type 'analyze image'"
        else:
            message=f"Sorry, I cannot process the image."

        dispatcher.utter_message(text=message)
        
        return []

class ActionCreatePDF(Action):
    
    API_ENDPOINT = 'http://127.0.0.1:8000'+'/createpdf'
    API_KEY = 'LambtonProject'


    def name(self) -> Text:
        return "action_create_pdf"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        slot_value = tracker.get_slot('user_name')
        
        if slot_value is not None:
        
            global U_DISEASE
            
            if U_DISEASE != "":
                disease = U_DISEASE
            else:
                disease = 'No Finding'
            
            headers = {
                "x-token": self.API_KEY,
                "Content-Type": "application/json"
            }
            
            payload = {
                "name": tracker.get_slot("user_name"),
                "age": tracker.get_slot("user_age"),
                "birth": tracker.get_slot("user_birth"),
                "address": tracker.get_slot("user_address"),
                "height": tracker.get_slot("user_height"),
                "weight": tracker.get_slot("user_weight"),
                "disease": disease
            }        
            # payload = {
            #     "name": "John Doe",
            #     "age": "30",
            #     "birth": "January 1, 1993",
            #     "address": "123 Main St, City, Country",
            #     "height": "180",
            #     "weight": "75",
            #     "disease": "mass"
            # }
            res = requests.request("POST", self.API_ENDPOINT, json=payload, headers=headers)
            print(payload)
            print(res.text)

            
            if res.status_code == 200:
                message=f"The PDF was created, if you want to download it, please write something like 'Show me the pdf'"
            else:
                message=f"Error creating PDF"

            dispatcher.utter_message(text=message)
        
        else:
            dispatcher.utter_message(text='To generate a PDF, I need the patient information, so write something like "I want to check an x-ray".')
        
        return []

