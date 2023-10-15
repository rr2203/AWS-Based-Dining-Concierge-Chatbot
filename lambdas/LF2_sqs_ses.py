import boto3
import json
import requests

# Initialize AWS clients
sqs = boto3.client('sqs')
dynamodb = boto3.resource('dynamodb')
ses = boto3.client('ses')
dynamodb_client = boto3.client('dynamodb')

queue_url = 'https://sqs.us-east-1.amazonaws.com/315615451600/suggestion'

def get_message_from_sqs():
    print("Fetching message from SQS.")
    response = sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=1)

    if 'Messages' in response:
        message = response['Messages'][0]
        message_body = json.loads(message['Body'])
        print(f"Received message: {message_body}")

        # delete the message from SQS
        # sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=message['ReceiptHandle'])
        print("Message deleted from SQS.")

        return message_body['Email'], message_body['Cuisine']
    return None, None

def query_elasticsearch_for_cuisine(cuisine):
    print(f"Querying Elasticsearch for cuisine: {cuisine}.")
    url = 'https://search-restaurants-vzgjpri2bsqcbj7qaslzx2cvvm.us-east-1.es.amazonaws.com/restaurants/_search?pretty'
    headers = {
        'Content-Type': 'application/json'
    }
    auth = ('haywire2210', 'RahulRaj1$')
    query = {
        "query": {
            "match": {
                "cuisine": cuisine
            }
        }
    }
    response = requests.get(url, headers=headers, auth=auth, data=json.dumps(query))

    if response.status_code == 200:
        results = response.json()
        ids = [hit['_id'] for hit in results['hits']['hits']]
        return ids
    else:
        print(f"Error {response.status_code}: {response.text}")
        return []



def dynamo_to_dict(item):
    """
    Convert DynamoDB item to python dict.
    """
    converted = {}
    for k, v in item.items():
        if 'S' in v:
            converted[k] = v['S']
        elif 'N' in v:
            converted[k] = float(v['N']) if '.' in v['N'] else int(v['N'])
        elif 'BOOL' in v:
            converted[k] = v['BOOL']
        # Add other data types if needed
    return converted

def get_restaurants_by_ids(restaurant_ids):
    print(f"Fetching restaurants with IDs: {restaurant_ids}.")
    
    keys = [{'id': {'S': rid}} for rid in restaurant_ids]
    response = dynamodb_client.batch_get_item(
        RequestItems={
            'yelp-restaurants': {
                'Keys': keys
            }
        }
    )

    # Convert the items fetched
    items = response['Responses']['yelp-restaurants']
    return [dynamo_to_dict(item) for item in items]




def send_email_to_user(email, restaurants):
    print(f"Sending email to {email}.")
    subject = "Restaurant Suggestions"
    body_lines = [f"Hello! Based on your preference, we suggest you try the following restaurants:"]
    for restaurant in restaurants:
        body_lines.append(f"{restaurant['name']} located at {restaurant['address']}.")
    body_lines.append("Enjoy your meal!")
    body = '\n'.join(body_lines)
    response = ses.send_email(
        Source='rr4185@nyu.edu',
        Destination={
            'ToAddresses': [email]
        },
        Message={
            'Subject': {'Data': subject},
            'Body': {'Text': {'Data': body}}
        }
    )
    return response


def lambda_handler(event, context):
    email, cuisine = get_message_from_sqs()
    if email and cuisine:
        restaurant_ids = query_elasticsearch_for_cuisine(cuisine)
        if restaurant_ids:
            # Fetch details of up to 5 restaurants
            restaurants = get_restaurants_by_ids(restaurant_ids[:5])
            
            # Send a consolidated email with all the suggestions
            send_email_to_user(email, restaurants)
            names = ', '.join([r['name'] for r in restaurants])
            print(f"Email sent to {email} with suggestions for restaurants: {names}.")
        else:
            print(f"No restaurants found for cuisine: {cuisine}")
    else:
        print("No messages in SQS.")


