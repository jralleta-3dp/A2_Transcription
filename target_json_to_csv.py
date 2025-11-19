import json
import csv

#import json file with given filepath
def json_to_csv(json_filepath, csv_filepath):
    try:
        with open(json_filepath, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
        
        names = []

        #loop through all objects in the json, append the target_name to the list
        for item in data:
            name = item.get("name", "")
            #remove special characters like (_,-,',)
            name = name.replace("(", "").replace(")", "").replace("'", "").replace("-", "").replace("_", "")
            names.append(name)

        # Open CSV file for writing names as comma separated values
        with open(csv_filepath, 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["Name"])  # Header row
            for name in names:
                writer.writerow([name])

    except Exception as e:
        print(f"❌ Error converting {json_filepath} to CSV: {e}")
        return False
    
json_to_csv('input.json', 'output.csv')