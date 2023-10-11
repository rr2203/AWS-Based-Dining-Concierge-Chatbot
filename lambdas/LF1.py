import json
import boto3

sqs = boto3.client('sqs')
queue_url = 'https://sqs.us-east-1.amazonaws.com/315615451600/suggestion'  # replace with your SQS queue URL

def lambda_handler(event, context):
    intent_name = event['currentIntent']['name']
    handlers = {
        "Greeting": handle_greeting,
        "ThankYou": handle_thank_you,
        "DiningSuggestions": handle_dining_suggestions
    }
    
    handler = handlers.get(intent_name)
    if handler:
        return handler(event)
    else:
        return default_response()

def handle_greeting(event):
    return create_response("Close", "Fulfilled", "Hi there, how can I help?")

def handle_thank_you(event):
    return create_response("Close", "Fulfilled", "You're welcome!")

def handle_dining_suggestions(event):
    location = event['currentIntent']['slots']['Location']
    cuisine = event['currentIntent']['slots']['Cuisine']
    dining_time = event['currentIntent']['slots']['DiningTime']
    number_of_people = event['currentIntent']['slots']['NumberOfPeople']
    email = event['currentIntent']['slots']['Email']
    
    slot_info = {
        'Location': location,
        'Cuisine': cuisine,
        'DiningTime': dining_time,
        'NumberOfPeople': number_of_people,
        'Email': email
    }
    
    if send_to_sqs(slot_info):
        message = f"Got it! Booking a {cuisine} restaurant in {location} at {dining_time} for {number_of_people} people. Details will be sent to {email}."
        return create_response("Close", "Fulfilled", message)
    else:
        return create_response("Close", "Failed", "Sorry about that, please try again later.")

def send_to_sqs(message_body):
    """Send a message to the SQS queue. Return True if successful, else False."""
    try:
        sqs.send_message(QueueUrl=queue_url, MessageBody=json.dumps(message_body))
        return True
    except Exception as e:
        print(f"Error sending message to SQS: {e}")
        return False

def default_response():
    return create_response("Close", "Fulfilled", "I'm sorry, I didn't understand that.")

def create_response(type, fulfillmentState, content):
    """Generate a dialogAction response with the given parameters."""
    return {
        "dialogAction": {
            "type": type,
            "fulfillmentState": fulfillmentState,
            "message": {
                "contentType": "PlainText",
                "content": content
            }
        }
    }
