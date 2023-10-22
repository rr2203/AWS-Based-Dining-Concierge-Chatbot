import boto3
import json
import requests

sqs = boto3.client('sqs')
ses = boto3.client('ses')
dynamodb_client = boto3.client('dynamodb')
queue_url = 'https://sqs.us-east-1.amazonaws.com/315615451600/suggestion'

def get_message_from_sqs():
    response = sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=1)
    print(f"SQS Response: {response}")
    if 'Messages' in response:
        message = response['Messages'][0]
        message_body = json.loads(message['Body'])
        sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=message['ReceiptHandle'])
        return message_body['Email'], message_body['Cuisine']
    return None, None

def query_elasticsearch_for_cuisine(cuisine):
    print(f"Querying Elasticsearch for cuisine: {cuisine}")
    url = 'https://search-restaurants-vzgjpri2bsqcbj7qaslzx2cvvm.us-east-1.es.amazonaws.com/restaurants/_search?pretty'
    headers = {'Content-Type': 'application/json'}
    auth = ('haywire2210', 'RahulRaj1$')
    query = {
        "query": {
            "match": {
                "cuisine": cuisine
            }
        }
    }
    response = requests.get(url, headers=headers, auth=auth, data=json.dumps(query))
    print(f"Elasticsearch response: {response.status_code}")
    if response.status_code == 200:
        results = response.json()
        ids = [hit['_id'] for hit in results['hits']['hits']]
        return ids
    return []

def dynamo_to_dict(item):
    converted = {}
    for k, v in item.items():
        if 'S' in v:
            converted[k] = v['S']
        elif 'N' in v:
            converted[k] = float(v['N']) if '.' in v['N'] else int(v['N'])
        elif 'BOOL' in v:
            converted[k] = v['BOOL']
    return converted

def get_restaurants_by_ids(restaurant_ids):
    print(f"Fetching restaurants by IDs: {restaurant_ids}")
    keys = [{'id': {'S': rid}} for rid in restaurant_ids]
    response = dynamodb_client.batch_get_item(RequestItems={'yelp-restaurants': {'Keys': keys}})
    print(f"DynamoDB batch_get_item response: {response}")
    items = response['Responses']['yelp-restaurants']
    return [dynamo_to_dict(item) for item in items]

def create_email_content(email, restaurants):
    body_lines = [f"Hello! Based on your preference, we suggest you try the following restaurants:"]
    for restaurant in restaurants:
        body_lines.append(f"{restaurant['name']} located at {restaurant['address']}.")
    body_lines.append("Enjoy your meal!")
    return '\n'.join(body_lines)

def store_restaurant_names_in_dynamodb(email, email_content):
    print(f"Storing restaurants for email: {email}")
    table_name = 'previous-searches'
    restaurant_names = email_content
    response = dynamodb_client.put_item(
        TableName=table_name,
        Item={
            'email': {'S': email},
            'restaurant_names': {'S': restaurant_names}
        }
    )
    print(f"DynamoDB put_item response: {response}")
    return response

def lambda_handler(event, context):
    print(f"Lambda handler invoked with event: {event}")
    email, cuisine = get_message_from_sqs()
    if email and cuisine:
        restaurant_ids = query_elasticsearch_for_cuisine(cuisine)
        if restaurant_ids:
            top_5_ids = restaurant_ids[:5]
            restaurants = get_restaurants_by_ids(top_5_ids)
            email_content = create_email_content(email, restaurants)
            store_restaurant_names_in_dynamodb(email, email_content)
            subject = "Restaurant Suggestions"
            print(f"Sending email to {email} with subject: {subject}")
            response = ses.send_email(
                Source='rr4185@nyu.edu',
                Destination={'ToAddresses': [email]},
                Message={'Subject': {'Data': subject},'Body': {'Text': {'Data': email_content}}}
            )
            print(f"SES send_email response: {response}")


