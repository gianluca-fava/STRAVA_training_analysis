import requests
import os
from dotenv import load_dotenv
import json

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
    data = requests.get(activites_url, headers=header, params=param, verify=True).json()

    file_path = "data.json"
    with open(file_path, 'w') as file:
        json.dump(data, file)

    print("Activities data has been successfully retrieved and saved to", file_path)

except requests.exceptions.RequestException as e:
    print("Error occurred during request:", e)

except KeyError as e:
    print("KeyError occurred:", e)

except Exception as e:
    print("An unexpected error occurred:", e)
