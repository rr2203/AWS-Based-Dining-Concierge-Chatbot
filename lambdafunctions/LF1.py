import json
import boto3

sqs = boto3.client('sqs')
ses = boto3.client('ses')
dynamodb_client = boto3.client('dynamodb')
queue_url = 'https://sqs.us-east-1.amazonaws.com/315615451600/suggestion'  # replace with your SQS queue URL

def lambda_handler(event, context):
    print(f"Lambda invoked with event: {event}")
    intent_name = event['currentIntent']['name']
    print(f"Intent name found: {intent_name}")
    
    handlers = {
        "ThankYou": handle_thank_you,
        "DiningSuggestions": handle_dining_suggestions,
        "Greeting": handle_greeting
    }
    
    handler = handlers.get(intent_name)
    if handler:
        return handler(event)
    else:
        print(f"No handler found for intent: {intent_name}")
        return default_response()


def handle_greeting(event):
    email = event['currentIntent']['slots']['email']

    # If email is provided, check for last searched content
    if email:
        last_searched_content = checkPreviousSearches(email)
        if last_searched_content:
            subject = "Previous Restaurant Suggestions"
            print(f"Sending email to {email} with subject: {subject}")
            response = ses.send_email(
                Source='rr4185@nyu.edu',
                Destination={'ToAddresses': [email]},
                Message={'Subject': {'Data': subject},'Body': {'Text': {'Data': last_searched_content}}}
            )
            print(f"SES send_email response: {response}")
            response_content = f"Hi! Your previously suggested recommendations were emailed to you.  How else can I assist you today?"
        else:
            response_content = f"Hi! I couldn't find any previous searches. How can I assist you today?"
        
        # Storing email in session attributes and sending the response
        return {
            "dialogAction": {
                "type": "ElicitIntent",
                "message": {
                    "contentType": "PlainText",
                    "content": response_content
                }
            },
            "sessionAttributes": {
                "userEmail": email
            }
        }
    else:
        return create_response("ElicitSlot", None, "Hi there! Please provide your email to proceed.")

def handle_thank_you(event):
    return create_response("Close", "Fulfilled", "You're welcome!")

def handle_dining_suggestions(event):
    email = event['sessionAttributes'].get('userEmail', None)
    if not email:   email = event['currentIntent']['slots']['Email']
    if not email:   return create_response("ElicitSlot", None, "Please provide your email to proceed.", "Email")

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
    print(f"Sending message to SQS: {message_body}")
    try:
        sqs.send_message(QueueUrl=queue_url, MessageBody=json.dumps(message_body))
        print(f"Message sent successfully to SQS.")
        return True
    except Exception as e:
        print(f"Error sending message to SQS: {e}")
        return False

def default_response():
    print("Entering default response")
    return create_response("Close", "Fulfilled", "I'm sorry, I didn't understand that.")


def create_response(type, fulfillmentState, content, slotToElicit=None):
    """Generate a dialogAction response with the given parameters."""
    response = {
        "dialogAction": {
            "type": type,
            "fulfillmentState": fulfillmentState,
            "message": {
                "contentType": "PlainText",
                "content": content
            }
        }
    }
    if slotToElicit:
        response["dialogAction"]["slotToElicit"] = slotToElicit
    return response

def checkPreviousSearches(email):
    table_name = 'previous-searches'
    print(f"Checking previous searches for email: {email}")
    
    try:
        response = dynamodb_client.get_item(
            TableName=table_name,
            Key={
                'email': {'S': email}
            }
        )
        print(f"DynamoDB response: {response}")
        
        if 'Item' in response:
            return response['Item']['restaurant_names']['S']
    except Exception as e:
        print(f"Error fetching restaurant_names from DynamoDB: {e}")
    return None
