import boto3
import json
import requests

# Initialize AWS clients
sqs = boto3.client('sqs')
dynamodb = boto3.resource('dynamodb')
ses = boto3.client('ses')

queue_url = 'https://sqs.us-east-1.amazonaws.com/315615451600/suggestion'

def get_message_from_sqs():
    print("Fetching message from SQS.")
    response = sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=1)

    if 'Messages' in response:
        message = response['Messages'][0]
        message_body = json.loads(message['Body'])
        print(f"Received message: {message_body}")

        # delete the message from SQS
        sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=message['ReceiptHandle'])
        print("Message deleted from SQS.")

        return message_body['Email'], message_body['Cuisine']
    return None, None

def query_elasticsearch_for_cuisine(cuisine):
    print(f"Querying Elasticsearch for cuisine: {cuisine}.")
    url = 'https://search-restaurants-vzgjpri2bsqcbj7qaslzx2cvvm.us-east-1.es.amazonaws.com/your_index_name/_search?pretty'
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

def get_restaurant_by_id(restaurant_id):
    print(f"Fetching restaurant with ID: {restaurant_id}.")
    table = dynamodb.Table('yelp-restaurants')

    try:
        response = table.get_item(Key={'id': restaurant_id})
    except Exception as e:
        print(str(e))
        return None

    return response.get('Item')

def send_email_to_user(email, restaurant):
    print(f"Sending email to {email}.")
    subject = "Restaurant Suggestion"
    body = f"Hello! We suggest you try {restaurant['name']} located at {restaurant['address']}. Enjoy your meal!"
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

email, cuisine = get_message_from_sqs()
if email and cuisine:
    restaurant_ids = query_elasticsearch_for_cuisine(cuisine)
    if restaurant_ids:
        restaurant = get_restaurant_by_id(restaurant_ids[0])
        if restaurant:
            send_email_to_user(email, restaurant)
            print(f"Email sent to {email} for restaurant {restaurant['name']}.")
        else:
            print(f"No restaurant found with ID: {restaurant_ids[0]}")
    else:
        print(f"No restaurants found for cuisine: {cuisine}")
else:
    print("No messages in SQS.")
