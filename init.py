import requests
import os
from dotenv import load_dotenv
import json
from datetime import datetime

'''
!!!! In the .env file there must be CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN.

First of all, the data of all the activities is downloaded, using the Strava API.
You will get a response: data.json which will contain the data, but a lot of things are missing for what I want to do.
So the only purpose of these requests is to get the activity ID so I can make a more precise request to the inside the activity itself.
'''

# Load environment variables from file .env
try:
    dotenv_path = os.path.join('PRIVATE', '.env')
    load_dotenv(dotenv_path)
    print('File .env read correctly')

except Exception as e:
    print(f"An error occurred while reading the .env file: {e}")

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
        'Authorization': 'Bearer ' + access_token} # Constructing the header with the access token for authorization

    # Setting parameters for the request to retrieve activities data
    param = {'per_page': 200, 'page': 1}

    data = requests.get(activites_url, headers=header, params=param, verify=True).json()

    with open("data.json", "w") as file:
        json.dump(data, file, indent=4)

    print("Activities data has been successfully retrieved")

except requests.exceptions.RequestException as e:
    print("Error occurred during request:", e) #handle any errors during the HTTP request

except KeyError as e:
    print("KeyError occurred:", e) #handle any errors when decoding the JSON response

except Exception as e:
    print("An unexpected error occurred:", e) #handle any other type of unexpected exception


'''
If everything was done correctly we should now have the data.json file which contains the list of all the activities.

We want to take the data only for the activities subsequent to the last saved one,
also because for each activity you need to make 2 requests and there is a risk of exceeding the daily maximum.
'''

# I open the just-created data.json and read the date of the last activity
with open('data.json', 'r') as file:
    data = json.load(file)

# I check if the file already exists and it's not void:
if os.path.exists('data_detailed.json') and os.path.getsize('data_detailed.json') > 2:

    print('data_detailed.json already exists')
    # open data_detailed.json
    with open('data_detailed.json', 'r') as file:
        data_detailed = json.load(file)

    # Remove the timezone part (Z) from the string and parse it
    last_activity_data_detailed = datetime.strptime(data_detailed[0]['start_date'][:-1], "%Y-%m-%dT%H:%M:%S")

    # check if the last dates activity of the 2 json are the same
    if last_activity_data_detailed != datetime.strptime(data[0]['start_date'][:-1], "%Y-%m-%dT%H:%M:%S"):

        '''
        if the 2 dates are different, it means that data_detailed is not updated.
        so I execute a request for each activity following the last one saved until we reach the first one in data.json

        -->the objective is to create a json with all the data (IDs) of data.json activities that have not yet been added to data_detailed
        as long as the date saved in data.json that i'm looking is  more recent than the last date in date_detailed, save that activity.

        (I make this check because data_detailed needs many requests to build up)
        '''

        # Append new activities to additional_data until we find one with start date before the last activity in data_detailed
        data_not_updated = []  # only the data following the last date in data_detailed

        i = 0
        while datetime.strptime(data[i]['start_date'][:-1], "%Y-%m-%dT%H:%M:%S") > last_activity_data_detailed:
            data_not_updated.append(data[i])
            i += 1

#if data_detialed does not exist, it must be created from 0, so epr all activities in data.json
else:
    data_not_updated = data

    # If it doesn't exist i create it
    data_detailed = []

    with open("data_detailed.json", "w") as file:
        json.dump(data_detailed, file)

    print('data_detailed.json created')


'''
Now let's move on to making requests for each activity on date:

I now have the whole list of activities to add in the main json (data_detailed.json).
So for each of these, I'm going to make a request to get the full details of the activity and one to get the uploaded pictures.
'''


try:
    for activity in data_not_updated:

        #(I use 'payload' and 'auth_url' from the previous requests)

        ID_activity = activity['id'] # get activity ID

        activity_detailed_url = f"https://www.strava.com/api/v3/activities/{ID_activity}"  # URL to get activity detailed
        activity_photos_url = f"https://www.strava.com/api/v3/activities/{ID_activity}/photos?size=1800%&photo_sources=true"  # URL to get all the photo uploaded in the activity

        # Sending a request to Strava to obtain permission
        res = requests.post(auth_url, data=payload, verify=True)
        res.raise_for_status()  # Raise an HTTPError for bad responses (4XX or 5XX)

        access_token = res.json()['access_token']

        header = {
            'Authorization': 'Bearer ' + access_token} # Constructing the header with the access token for authorization

        # Setting parameters for the request to retrieve activities data
        param = {'per_page': 200, 'page': 1}

        # Make requests API
        response_activity_detailed = requests.get(activity_detailed_url, headers=header, params=param, verify=True)
        response_activity_photos = requests.get(activity_photos_url, headers=header, params=param, verify=True)

        # I have to insert the data of the single activity into the json of the detailed activity, to have a unique one:

        # Check the answers and save the data in the corresponding files
        if response_activity_photos.status_code == 200:

            data_photo = response_activity_photos.json()

            if response_activity_detailed.status_code == 200:

                data_activity = response_activity_detailed.json()
                data_activity['photos'] = data_photo  # replaces the contents of 'photos' with the correct photo details (we need the links)

                if 'Ferrata' in activity['name']:
                    data_activity['color'] = 'red'
                else:
                    data_activity['color'] = 'blue'

                data_detailed.insert(0, data_activity) #add the new data on top of the others

                #since there are so many requests to be made, it is likely that they cannot all be done in one run, so I save each time
                with open("data_detailed.json", "w") as file:
                    json.dump(data_detailed, file, indent=4)

            else:
                print("Error in query activity_detailed")
                exit()

        else:
            print("Error in query activity_photos")
            exit()

    print('data_detailed saved correctly')

except requests.exceptions.RequestException as e:
    print(f"An error occurred during the HTTP request: {e}")

except json.JSONDecodeError as e:
    print(f"An error occurred while decoding JSON response: {e}")

except Exception as e:
    print(f"An unexpected error occurred: {e}")

