import boto3

dynamodb = boto3.resource('dynamodb')


def get_restaurant_by_id(restaurant_id):
    table = dynamodb.Table('yelp-restaurants')

    try:
        response = table.get_item(Key={'id': restaurant_id})
    except ClientError as e:
        print(e.response['Error']['Message'])
        return None

    # If the item is found, the response will contain an 'Item' key.
    return response.get('Item')


# Example Usage:
restaurant_id = "C3tP0fNNAoxOAC3O406CXQ"
restaurant = get_restaurant_by_id(restaurant_id)
if restaurant:
    print(restaurant)
else:
    print(f"No restaurant found with ID: {restaurant_id}")
