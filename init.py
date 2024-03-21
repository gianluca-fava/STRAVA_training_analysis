import requests
import os
from dotenv import load_dotenv
import json
from datetime import datetime
from random import randrange

## READ .env

# Load environment variables from file .env
dotenv_path = os.path.join('PRIVATE', '.env')
load_dotenv(dotenv_path)

print('File .env read correctly')

# Construct the payload using environment variables
payload = {
    'client_id': os.getenv('CLIENT_ID'),
    'client_secret': os.getenv('CLIENT_SECRET'),
    'refresh_token': os.getenv('REFRESH_TOKEN'),
    'grant_type': "refresh_token",
    'f': 'json'
}

auth_url = "https://www.strava.com/oauth/token"  # URL for requesting authorization token from Strava
activites_url = "https://www.strava.com/api/v3/athlete/activities"  # URL for retrieving activities data from Strava API

try:
    # Sending a request to Strava to obtain permission
    res = requests.post(auth_url, data=payload, verify=True)
    res.raise_for_status()  # Raise an HTTPError for bad responses (4XX or 5XX)

    access_token = res.json()['access_token']

    header = {
        'Authorization': 'Bearer ' + access_token}  # Constructing the header with the access token for authorization

    # Setting parameters for the request to retrieve activities data
    param = {'per_page': 200, 'page': 1}

    new_data = requests.get(activites_url, headers=header, params=param, verify=True).json()

    print("Activities data has been successfully retrieved")

except requests.exceptions.RequestException as e:
    print("Error occurred during request:", e)

except KeyError as e:
    print("KeyError occurred:", e)

except Exception as e:
    print("An unexpected error occurred:", e)

with open('data.json', 'r') as file:
    existing_data = json.load(file)
    if existing_data:
        last_activity_date = datetime.strptime(existing_data[0]['start_date'][:-1],
                                               "%Y-%m-%dT%H:%M:%S")  # Remove the timezone part (Z) from the string and parse it

# check if the 2 date are different otherwise it's a mess
if datetime.strptime(new_data[0]['start_date'][:-1], "%Y-%m-%dT%H:%M:%S") != last_activity_date:
    # Append new activities to additional_data until we find one with start date before the last activity in existing data
    additional_data = []  # only the data following the last date in data
    i = 0
    while datetime.strptime(new_data[i]['start_date'][:-1], "%Y-%m-%dT%H:%M:%S") > last_activity_date:
        additional_data.append(new_data[i])
        i += 1

    # Add random color to all the activities (for the plot in the map)
    for activity in additional_data:
        activity["color"] = "#{:02x}{:02x}{:02x}".format(randrange(255), randrange(255), randrange(255))

    data_extended = additional_data + existing_data

    # Overwrite json
    with open("data.json", "w") as file:
        json.dump(data_extended, file, indent=4)