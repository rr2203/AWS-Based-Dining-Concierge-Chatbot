import requests
import json

# Yelp API Configuration
API_KEY = "_La5lkh4_RMzNFhyAcqnyIby1_zXjaVrUxVWHIiaAkOPC1x24dt-nvW_fAgMDaBXkQ7MJjaz65hoD7q4pXehPmMr_j4sE6nJlNS4GDjxHJ9oDjqQNwtepJPcFM0lZXYx"
BASE_URL = "https://api.yelp.com/v3/businesses/search"
HEADERS = {
    "Authorization": "Bearer " + API_KEY
}

def get_restaurants_for_cuisine(cuisine):
    params = {
        "term": cuisine,
        "location": "Manhattan, NY",
        "limit": 50,
        "offset": 0
    }
    response = requests.get(BASE_URL, headers=HEADERS, params=params)
    if response.status_code != 200:
        print(
            f"Failed to retrieve data for {cuisine}. Status code: {response.status_code}")
        return []

    data = response.json()
    return data['businesses']

def fetch_all_restaurants():
    all_restaurants = []
    cuisines = ["Chinese", "Mexican", "Italian"]

    for cuisine in cuisines:
        all_restaurants.extend(get_restaurants_for_cuisine(cuisine))

    # Save the collected restaurants to a JSON file
    with open('manhattan_restaurants.json', 'w') as file:
        json.dump(all_restaurants, file)

    print(f"Total restaurants collected: {len(all_restaurants)}")

if __name__ == "__main__":
    fetch_all_restaurants()
