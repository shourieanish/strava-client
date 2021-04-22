import json
import requests
import time
import numpy as np


class Strava_Client:


   def __init__(self, client_id, client_secret):
      
      self.client_id = client_id
      self.client_secret = client_secret

   
   def strava_connection(self):

      # Get the tokens from file to connect to Strava
      with open('Strava_CreateManualActivity.json') as json_file:
         strava_tokens = json.load(json_file)

      # If access_token has expired, then use the refresh_token to get the new access_token
      if strava_tokens['expires_at'] < time.time():
         response = requests.post(
                     url = 'https://www.strava.com/oauth/token',
                     data = {
                              'client_id'     : self.client_id,
                              'client_secret' : self.client_secret,
                              'grant_type'    : 'refresh_token',
                              'refresh_token' : strava_tokens['refresh_token']
                              }
                     )

         # Save response as json in new variable (refresh token is updated)
         new_strava_tokens = response.json()

         # Save new tokens to a file
         with open('Strava_CreateManualActivity.json', 'w') as outfile:
            json.dump(new_strava_tokens, outfile)

         # Use new Strava tokens
         strava_tokens = new_strava_tokens

      access_token = strava_tokens['access_token']

      return access_token


   def fix_inputs(self, dist, duration):

      dist = dist / 0.00062137119224

      d_temp = duration.split(':')
      d_temp.reverse()
      d_time = 0
      i = 0

      for t in d_temp:
         if i==0:
            d_time += int(t)
         elif i==1:
            d_time += 60*int(t)
         elif i==2:
            d_time += 3600*int(t)

         i += 1


      return str(dist), str(d_time)



   def create_activity(self, name="Activity", start_datetime='', duration='', description='', activity_type='run', dist=0, trainer=0, commute=0):

      dist, duration = self.fix_inputs(dist, duration)

      upload_url = 'https://www.strava.com/api/v3/activities'
      header       = { 'Authorization': 'Bearer ' + self.strava_connection() }
      payload      = {
                     'name'             : name,
                     'description'      : description,
                     'type'             : activity_type,
                     'start_date_local' : start_datetime,
                     'elapsed_time'     : duration,
                     'distance'         : dist,
                     'trainer'          : trainer,
                     'commute'          : commute,
                     }

      try:
         new_activity = requests.post(upload_url, headers=header, data=payload).json()
         print(new_activity)

      except requests.ConnectionError as e:
         print("  Unable to create the manual activity.")
         print(str(e))
         print("")

      return


   def upload_gpx(self, file_path, name="Activity", description='', activity_type='run', trainer=0, commute=0):

      file_path = 'runkeeper_data/' + file_path
      activity_file = open(file_path, 'r')

      upload_url = 'https://www.strava.com/api/v3/uploads'
      header       = { 'Authorization': 'Bearer ' + self.strava_connection() }
      payload      = {
                     'name'             : name,
                     'description'      : description,
                     'data_type'        : 'gpx',
                     'activity_type'    : 'run',
                     'trainer'          : trainer,
                     'commute'          : commute
                     }


      try:
         new_activity = requests.post(upload_url, headers=header, files={'file': activity_file}, params=payload).json()
         print(new_activity)

      except requests.ConnectionError as e:
         print("  Unable to create the manual activity.")
         print(str(e))
         print("")

      return


