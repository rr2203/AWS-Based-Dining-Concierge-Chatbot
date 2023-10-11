from decimal import Decimal
import boto3
import json
import time

dynamodb = boto3.resource('dynamodb')


def delete_table_if_exists(table_name):
    """
    Delete the specified DynamoDB table if it exists.
    """
    client = boto3.client('dynamodb')
    try:
        client.describe_table(TableName=table_name)
        print(f"Deleting table {table_name}...")
        client.delete_table(TableName=table_name)

        # Wait for the table to be deleted
        waiter = client.get_waiter('table_not_exists')
        waiter.wait(TableName=table_name)
        print(f"Table {table_name} deleted.")
    except client.exceptions.ResourceNotFoundException:
        pass


def create_dynamodb_table():
    table = dynamodb.create_table(
        TableName='yelp-restaurants',
        KeySchema=[
            {
                'AttributeName': 'id',
                'KeyType': 'HASH'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'id',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )

    # Wait until the table is created
    table.meta.client.get_waiter('table_exists').wait(
        TableName='yelp-restaurants')


def batch_insert_into_dynamodb():
    with open('manhattan_restaurants.json', 'r') as file:
        all_restaurants = json.load(file)

    print(f"Attempting to insert {len(all_restaurants)} restaurants...")

    # Split the restaurants into batches of 25 (DynamoDB's limit for batch_write_item)
    batches = [all_restaurants[i:i + 25]
               for i in range(0, len(all_restaurants), 25)]

    for batch in batches:
        with dynamodb.Table('yelp-restaurants').batch_writer() as batch_writer:
            for restaurant in batch:
                data = {
                    'id': restaurant['id'],
                    'name': restaurant['name'],
                    'address': restaurant['location']['address1'],
                    'coordinates': {
                        'latitude': Decimal(str(restaurant['coordinates']['latitude'])),
                        'longitude': Decimal(str(restaurant['coordinates']['longitude']))
                    },
                    'review_count': restaurant['review_count'],
                    'rating': Decimal(str(restaurant['rating'])),
                    'zip_code': restaurant['location']['zip_code'],
                    # UTC time
                    'insertedAtTimestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
                }
                batch_writer.put_item(Item=data)
                print(f"Inserted restaurant: {restaurant['name']}")

    print("Insertion complete.")


if __name__ == "__main__":
    # Read from JSON, delete table if it exists, create it again, and insert data using batch writes
    delete_table_if_exists('yelp-restaurants')
    create_dynamodb_table()
    batch_insert_into_dynamodb()
