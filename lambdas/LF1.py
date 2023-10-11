import json


def lambda_handler(event, context):
    intent_name = event['currentIntent']['name']

    if intent_name == "Greeting":
        return {
            "dialogAction": {
                "type": "Close",
                "fulfillmentState": "Fulfilled",
                "message": {
                    "contentType": "PlainText",
                    "content": "Hi there, how can I help?"
                }
            }
        }
    elif intent_name == "ThankYou":
        return {
            "dialogAction": {
                "type": "Close",
                "fulfillmentState": "Fulfilled",
                "message": {
                    "contentType": "PlainText",
                    "content": "You're welcome!"
                }
            }
        }
    elif intent_name == "DiningSuggestions":
        # Handle the logic to provide dining suggestions based on the slots.
        location = event['currentIntent']['slots']['Location']
        cuisine = event['currentIntent']['slots']['Cuisine']
        dining_time = event['currentIntent']['slots']['DiningTime']
        number_of_people = event['currentIntent']['slots']['NumberOfPeople']
        email = event['currentIntent']['slots']['Email']

        # For now, just respond with a confirmation.
        return {
            "dialogAction": {
                "type": "Close",
                "fulfillmentState": "Fulfilled",
                "message": {
                    "contentType": "PlainText",
                    "content": f"Got it! Booking a {cuisine} restaurant in {location} at {dining_time} for {number_of_people} people. Details will be sent to {email}."
                }
            }
        }
