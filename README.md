## The aim is to create a method/framework for analysing one's training on Strava.

First you have to register with the Strava API:
https://www.strava.com/settings/api

(You will have 100 queries every 15 minutes with a maximum of 1000 per day).

For the configuration you have to create an .env file (I put it in the PRIVATE folder where I had to put other things so that I could ignore them with the gitignore) this file should look like this:
CLIENT_ID=XXXX
CLIENT_SECRET=XXXXXXXXX
REFRESH_TOKEN=XXXXXXXXX
