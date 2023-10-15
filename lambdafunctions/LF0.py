import boto3
import json

def lambda_handler(event, context):
    client = boto3.client('lex-runtime')

    # Logging: Print event for debugging
    print("Received event:", event)

    body = json.loads(event['body'])
    inputText = body['messages'][0]['unstructured']['text']

    # Logging: Print the extracted inputText
    print("Input text extracted:", inputText)

    try:
        response = client.post_text(
            botName='Concierge',
            botAlias='Stage',
            userId='rahul',
            inputText=inputText,
            sessionAttributes={}
        )

        # Logging: Print Lex response
        print("Received response from Lex:", response)

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
        # Logging: Print the exception for debugging
        print("Exception encountered:", e)

        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            'body': json.dumps(str(e))
        }
