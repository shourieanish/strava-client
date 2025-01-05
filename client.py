import json
import requests
import time


class StravaClient:

    def __init__(self, client_id, client_secret):
        self._oauth_uri = 'https://www.strava.com/oauth/token'
        self._base_url = 'https://www.strava.com/api/v3'
        self._tokens = None
        self._updated_tokens = None
        self._client_id = client_id
        self._client_secret = client_secret

    def get_access_token(self):
        """
        Get access token
        """
        if self._updated_tokens:
            return self._updated_tokens['access_token']
        else:
            return self._tokens['access_token']

    def get_tokens(self, config_path):
        """
        Get tokens from config file
        """
        with open(config_path, 'r') as f:
           self._tokens = json.load(f)

    def create_access_token(self, auth_code):
        """
        Creating a new access token using an authentication code
        """

        response = requests.post(
            url=self._oauth_uri,
            data={
                'client_id': self._client_id,
                'client_secret': self._client_secret,
                'grant_type': 'authorization_code',
                'code': auth_code
            }
        )
        response.raise_for_status()

        self._updated_tokens = response.json()


    def authenticate(self):
        """
        Checking if access token is valid.
        If access_token has expired, then use the refresh_token to get the new access_token
        """

        if self._tokens.get('expires_at', 0) < time.time():
            response = requests.post(
                url = self._oauth_uri,
                data = {
                    'client_id'     : self._client_id,
                    'client_secret' : self._client_secret,
                    'grant_type'    : 'refresh_token',
                    'refresh_token' : self._tokens['refresh_token']
                }
            )
            response.raise_for_status()

            self._updated_tokens = response.json()

    def save_tokens(self, config_path):
        """
        Save tokens if updated
        """
        if self._updated_tokens:
            with open(config_path, 'w') as f:
                json.dump(self._updated_tokens, f)

    def create_activity(self,
                        name,
                        type,
                        start_date_local,
                        elapsed_time,
                        distance,
                        description='',
                        trainer=0,
                        commute=0):
        """
        Creating an activity without a GPX file
        :param name: activity name
        :param type: activity type (e.g. "run")
        :param start_date_local: start datetime
        :param elapsed_time: activity time
        :param distance: activity distance
        :param description: text description of activity
        :param trainer: boolean representing trainer activity
        :param commute: boolean representing commute
        """
        endpoint = 'activities'
        url = f'{self._base_url}/{endpoint}'
        header = {'Authorization': f"Bearer {self.get_access_token()}"}
        payload = {
            'name': name,
            'description': description,
            'type': type,
            'start_date_local': start_date_local,
            'elapsed_time': elapsed_time,
            'distance': distance,
            'trainer': trainer,
            'commute': commute,
        }

        try:
            r = requests.post(url, headers=header, data=payload)
            r.raise_for_status()
            activity = r.json()
            print(f"Created activity {activity['id']}")

        except Exception as e:
            print(f"Unable to create the manual activity {payload}.")
            print(e)
            print()

    def upload_activity(self,
                        file,
                        name,
                        description='',
                        activity_type='run',
                        data_type = 'gpx',
                        trainer=0,
                        commute=0):
        """
        :param file: gpx file contents
        :param name: activity name
        :param description: text description of activity
        :param activity_type: type of activity (e.g. "run")
        :param data_type: data type of file contents
        :param trainer: boolean representing trainer activity
        :param commute: boolean representing commute
        """

        header = {'Authorization': f"Bearer {self.get_access_token()}"}
        payload = {
            'name': name,
            'description': description,
            'data_type': data_type,
            'activity_type': activity_type,
            'trainer': trainer,
            'commute': commute
        }

        endpoint = 'uploads'
        url = f'{self._base_url}/{endpoint}'

        try:
            r = requests.post(url,
                              headers=header,
                              files={'file': file},
                              params=payload)
            r.raise_for_status()
            activity = r.json()
            print(f"Created activity upload {activity['id']}")

        except Exception as e:
            print(f"Unable to create the manual activity {payload}.")
            print(e)
            print()