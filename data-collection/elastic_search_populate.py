import json
import os

# Get the directory in which this script resides
script_directory = os.path.dirname(os.path.abspath(__file__))

# Path to the input and output JSON files
input_path = os.path.join(script_directory, 'static', 'yelp_restaurants.json')
output_path = os.path.join(script_directory, 'static', 'es.json')

# Step 1: Read the JSON data
with open(input_path, 'r') as file:
    data = json.load(file)

# Step 2: Convert to Elasticsearch bulk load format
es_data = []
for entry in data:
    index_data = {
        "index": {
            "_index": "your_index_name",  # Replace with your actual index name
            "_id": entry['id']
        }
    }
    es_data.append(index_data)
    es_data.append({"cuisine": entry['cuisine']})

# Step 3: Save the converted data
with open(output_path, 'w') as file:
    for item in es_data:
        json.dump(item, file)
        file.write('\n')

print("Data conversion completed. Ready for Elasticsearch bulk loading.")