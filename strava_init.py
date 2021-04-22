# Necessary libraries
import json
import pandas
import requests
import sys
import time

# Necessary variables
# Copy these over from https://www.strava.com/settings/api and from step #6
# above
strava_client_id     = ''
strava_client_secret = ''
strava_client_code   = ''

# Make Strava auth API call with client_id, client_secret and code
response = requests.post(
             url = 'https://www.strava.com/oauth/token',
             data = {
                      'client_id'    : strava_client_id,
                      'client_secret': strava_client_secret,
                      'code'         : strava_client_code,
                      'grant_type'   : 'authorization_code'
                    }
           )

# Save json response as a variable
strava_tokens = response.json()

# Save tokens to file
with open('Strava_CreateManualActivity.json', 'w') as outfile:
    json.dump(strava_tokens, outfile)

# Open JSON file and print the file contents to check it's worked properly
with open('Strava_CreateManualActivity.json') as check:
  strava_tokens = json.load(check)

print(strava_tokens)
