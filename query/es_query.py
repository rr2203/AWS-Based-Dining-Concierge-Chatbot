import requests
import json

def query_elasticsearch_for_cuisine(cuisine):
    url = 'https://search-restaurants-vzgjpri2bsqcbj7qaslzx2cvvm.us-east-1.es.amazonaws.com/your_index_name/_search?pretty'
    headers = {
        'Content-Type': 'application/json'
    }
    auth = ('haywire2210', 'RahulRaj1$')  # your username and password
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

# Test
cuisine_to_search = "Chinese"
ids = query_elasticsearch_for_cuisine(cuisine_to_search)
print(f"Found restaurants with IDs: {ids} for cuisine {cuisine_to_search}")
