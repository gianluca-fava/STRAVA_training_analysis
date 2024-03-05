## The aim is to create a method/framework for analysing one's training on Strava.

To get full access to the Strava API, follow this guide:
https://developers.strava.com/docs/getting-started/
First you have to register with the Strava API:
https://www.strava.com/settings/api

(You will have 100 queries every 15 minutes with a maximum of 1000 per day).



### Postmat

Then you'll need to log in to Postmat to access the requests:
https://web.postman.co/workspace

(Advice on Postmat, make each POST/GET call in a different tab)

To access all activities, follow these steps:

1) Get authorization code from the authorization page. This is a one-time, manual step. !!!Change YOUR_CLIENT_ID with yours (you can find it in https://www.strava.com/settings/api)
   
https://www.strava.com/oauth/authorize?client_id=YOUR_CLIENT_ID&redirect_uri=http://localhost&response_type=code&scope=activity:read_all

3) The page will not give any result, but in the URL there will be code = XXXXXXXX, copy that code:
   
http://localhost/?state=&code=XXXXXXXXXXXXX&scope=read,activity:read_all

5) Exchange: YOUR_CLIENT_ID, YOUR_CLIENT_SECRET, YOUR_CODE_FROM_PREVIOUS_STEP (do not look for it in the browser)
   
https://www.strava.com/oauth/token?client_id=YOUR_CLIENT_ID&client_secret=YOUR_CLIENT_SECRET&code=YOUR_CODE_FROM_PREVIOUS_STEP&grant_type=authorization_code

7) In Postmat, make a new request with POST and paste the link created in step 5) and take from the response "access_token": XXXXXXXX and "refresh_token": YYYYYYY (it will be needed later)

8) Exchange: ACCESS_TOKEN_PREVIOUS_STEP

https://www.strava.com/api/v3/athlete/activities?access_token=ACCESS_TOKEN_PREVIOUS_STEP

6) Make a new GET request in Postmat with the link created in step 5) to get the list of all activities

7) Exchange: YOUR_CLIENT_ID, YOUR_CLIENT_SECRET, YOUR_REFRESH_TOKEN_PREVIOUS_STEP (the "refresh_token": YYYYYYY from step 4))

https://www.strava.com/oauth/token?client_id=YOUR_CLIENT_ID&client_secret=YOUR_CLIENT_SECRET&refresh_token=YOUR_REFRESH_TOKEN_PREVIOUS_STEP&grant_type=refresh_token

8) New POST request with the link from point 7) will save 'refresh_token' : ZZZZZZ which will be the new and final token to make updates when new activities are uploaded


### Configuration

For the configuration you have to create an .env file (I put it in the PRIVATE folder where I had to put other things so that I could ignore them with the gitignore) this file should look like this (the REFRESH_TOKEN is the one taken from step 8) above):

CLIENT_ID=XXXX
CLIENT_SECRET=XXXXXXXXX
REFRESH_TOKEN=XXXXXXXXX
