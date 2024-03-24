import requests
import os
from dotenv import load_dotenv
import json
from datetime import datetime
import random


'''
!!!! In the .env file there must be CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN !!!!
'''
try:
    dotenv_path = os.path.join('PRIVATE', '.env')
    load_dotenv(dotenv_path)
    print('File .env read correctly')

except Exception as e:
    print(f"An error occurred while reading the .env file: {e}")


#request_data: makes the request to the Strava API, requests the URL
def request_data(url):
    try:
        # Construct the payload using environment variables
        payload = {
            'client_id': os.getenv('CLIENT_ID'),
            'client_secret': os.getenv('CLIENT_SECRET'),
            'refresh_token': os.getenv('REFRESH_TOKEN'),
            'grant_type': "refresh_token",
            'f': 'json'
        }

        auth_url = "https://www.strava.com/oauth/token"  # URL for requesting authorization token from Strava

        # Sending a request to Strava to obtain permission
        res = requests.post(auth_url, data=payload, verify=True)
        res.raise_for_status()  # Raise an HTTPError for bad responses (4XX or 5XX)

        access_token = res.json()['access_token']

        header = {
            'Authorization': 'Bearer ' + access_token}  # Constructing the header with the access token for authorization

        # Setting parameters for the request to retrieve activities data
        param = {'per_page': 200, 'page': 1}

        # Make requests API
        response_activity = requests.get(url, headers=header, params=param, verify=True)

        return response_activity

    except requests.exceptions.RequestException as e:
        print("Error occurred during request:", e)  # handle any errors during the HTTP request

    except KeyError as e:
        print("KeyError occurred:", e)  # handle any errors when decoding the JSON response

    except Exception as e:
        print("An unexpected error occurred:", e)  # handle any other type of unexpected exception




'''
First of all, the data of all the activities is downloaded, using the Strava API.
You will get a response: data.json which will contain the data, but a lot of things are missing for what I want to do.
So the only purpose of these requests is to get the activity ID so I can make a more precise request to the inside the activity itself.
'''

activites_url = "https://www.strava.com/api/v3/athlete/activities"  # URL for retrieving activities data from Strava API

data = request_data(activites_url).json()

#save data.json
with open("Data/data.json", "w") as file:
    json.dump(data, file, indent=4)

print("Activities data has been successfully retrieved")



'''
We want to take the data only for the activities subsequent to the last saved one,
also because for each activity you need to make 2 requests and there is a risk of exceeding the daily maximum.
'''

# I open the just-created data.json and read the date of the last activity
with open('Data/data.json', 'r') as file:
    data = json.load(file)

# I check if the file already exists and it's not void:
if os.path.exists('Data/data_detailed.json') and os.path.getsize('Data/data_detailed.json') > 2:

    data_not_updated = []  # only the data following the first (most recent) date in data_detailed
    old_data_not_loaded = [] # only the data following the last (less recent) date in data_detailed

    print('data_detailed.json already exists')
    # open data_detailed.json
    with open('Data/data_detailed.json', 'r') as file:
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

        print('Found items with a date later than the last saved')

        # Append new activities to additional_data until we find one with start date before the last activity in data_detailed
        i = 0
        while datetime.strptime(data[i]['start_date'][:-1], "%Y-%m-%dT%H:%M:%S") > last_activity_data_detailed:
            data_not_updated.append(data[i])
            i += 1


    '''
    We must also check that the last date of date_detailed is equal to the date in date.
    This can happen when running init.py for the first time and you have many tasks in data.json and therefore cannot execute everything at once.
    I then create a new list containing the files to be placed at the bottom:
    '''

    first_activity_data_detailed = datetime.strptime(data_detailed[len(data_detailed) - 1]['start_date'][:-1],"%Y-%m-%dT%H:%M:%S")

    if first_activity_data_detailed != datetime.strptime(data[len(data) - 1]['start_date'][:-1], "%Y-%m-%dT%H:%M:%S"):

        print('Found items with a date prior to the last saved date')

        i = len(data) - 1
        while datetime.strptime(data[i]['start_date'][:-1], "%Y-%m-%dT%H:%M:%S") < first_activity_data_detailed:
            old_data_not_loaded.append(data[i])
            i -= 1

#if data_detailed does not exist, it must be created as void, so we need to insert all activities in data.json
else:
    data_not_updated = data
    old_data_not_loaded = [] #we need only the data_not_updated in this case

    # If it doesn't exist I create it
    data_detailed = []

    with open("Data/data_detailed.json", "w") as file:
        json.dump(data_detailed, file)

    print('data_detailed.json created')

'''
Function to determine the colour of the activity, choose from a personally chosen list
'''


def generate_color(color_in):
    if color_in == 'red':
        # types of red to choose from
        type_of_red = ["#DF2424", '#B01111', '#9E0F0F', '#EC4040', '#FF0000', '#BC0000', '#A42B2B']

        # Random selection of a red type in HEX format
        casual_index = random.randint(0, len(type_of_red) - 1)
        color = type_of_red[casual_index]


    elif color_in == 'blue':
        # types of red to choose from
        type_of_blue = ['#0036FF', '#082DB8', '#2A51DF', '#032397', '#0000FF', '#1356B8', '#0C0574']

        # Random selection of a red type in HEX format
        casual_index = random.randint(0, len(type_of_blue) - 1)
        color = type_of_blue[casual_index]

    return color


'''
Now let's move on to making requests for each activity on data:

I now have the whole list of activities to add in the main json (data_detailed.json).
So for each of these, I'm going to make a request to get the full details of the activity and one to get the uploaded pictures.
'''

def add_activity_data_detailed(ID_activity, position):
    try:
        activity_detailed_url = f"https://www.strava.com/api/v3/activities/{ID_activity}"  # URL to get activity detailed
        activity_photos_url = f"https://www.strava.com/api/v3/activities/{ID_activity}/photos?size=1800%&photo_sources=true"  # URL to get all the photo uploaded in the activity

        # I have to insert the data of the single activity into the json of the detailed activity, to have a unique one:
        response_activity_detailed = request_data(activity_detailed_url)
        response_activity_photos = request_data(activity_photos_url)

        # Check the answers and save the data in the corresponding files
        if response_activity_photos.status_code == 200 and response_activity_detailed.status_code == 200:

            data_photo = response_activity_photos.json()
            data_activity = response_activity_detailed.json()

            data_activity['photos'] = data_photo  # replaces the contents of 'photos' with the correct photo details (we need the links)

            #my interest is to differentiate Via Ferrata from normal hike so I change the colour
            if 'Ferrat' in activity['name']:
                data_activity['color'] = generate_color('red')
            else:
                data_activity['color'] =  generate_color('blue')

            #I position the data correctly according to whether it goes at the top or at the bottom
            if position == 'bottom':
                data_detailed.append(data_activity)  # add the new data on top of the others
            elif position == 'top':
                data_detailed.insert(0, data_activity)

            # since there are so many requests to be made, it is likely that they cannot all be done in one run, so I save each time
            with open("Data/data_detailed.json", "w") as file:
                json.dump(data_detailed, file, indent=4)

        else:
            print("Error in query activity_photos/activity_detailed")
            exit()

    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the HTTP request: {e}")

    except json.JSONDecodeError as e:
        print(f"An error occurred while decoding JSON response: {e}")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")


# Utilizza islice per iterare solo sulle prime tre attività in data_not_updated
for activity in reversed(data_not_updated):
    ID_activity = activity['id']  # Ottieni l'ID dell'attività
    add_activity_data_detailed(ID_activity, 'top')

for activity in reversed(old_data_not_loaded):
    ID_activity = activity['id']  # get activity ID
    add_activity_data_detailed(ID_activity, 'bottom')

print('data_detailed saved correctly')


'''
save 49 activities each time it is executed (100 requests available):
- 1 request data.json (general)
- 49 request data_detailed.json (for the activity)
- 49 request data_detailed.json (for the photo)
'''
