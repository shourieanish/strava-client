import pandas as pd
from strava_functions import Strava_Client

strava_client_id     = ''
strava_client_secret = ''

strava = Strava_Client(strava_client_id, strava_client_secret)

data = pd.read_csv("runkeeper_data/cardioActivities1.csv")
data['Duration'] = data['Duration'].astype(str)
data['Date'] = pd.to_datetime(data['Date'])

for index, row in data.iterrows():

	if isinstance(row['GPX File'], str):
		strava.upload_gpx(row['GPX File'], name=row['Activity Id'], description=row['Notes'])
	else:
		strava.create_activity(name=row['Activity Id'], start_datetime=row['Date'],
			description=row['Notes'], dist=row['Distance (mi)'], duration=row['Duration'])



