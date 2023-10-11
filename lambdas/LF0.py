import boto3
import json


def lambda_handler(event, context):
    print("yolo")
    print(event)
    client = boto3.client('lex-runtime')

    # Extract the inputText from the event body
    body = json.loads(event['body'])
    inputText = body['messages'][0]['unstructured']['text']

    try:
        response = client.post_text(
            botName='Concierge',
            botAlias='Stage',
            userId='rahul',  # Unique ID for the user
            inputText=inputText,  # Use extracted inputText from event
            sessionAttributes={}
        )

        # Transform Lex response into expected format
        transformed_response = {
            'messages': [{
                'type': 'unstructured',
                'unstructured': {
                    'text': response['message']
                }
            }]
        }

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            'body': json.dumps(transformed_response)
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            'body': json.dumps(str(e))
        }
