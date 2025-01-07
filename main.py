import os
import sys
import zipfile
import argparse
import pandas as pd

from client import StravaClient


MILES_PER_METER = 0.00062137119224


def time_to_seconds(time_str):
    parts = time_str.split(':')
    if len(parts) == 3:
        hours, minutes, seconds = map(int, parts)
        return hours * 3600 + minutes * 60 + seconds
    elif len(parts) == 2:
        minutes, seconds = map(int, parts)
        return minutes * 60 + seconds
    else:
        print("Unexpected input for activity duration")
        sys.exit(1)


def main():
    """
    Get data from Runkeeper export file and posts to Strava API
    """

    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')
    config_file = os.getenv('STRAVA_CONFIG_PATH')

    parser = argparse.ArgumentParser(description="A script to demonstrate argparse usage.")

    parser.add_argument(
        "--create-access-token",
        action="store_true",
        help="Create a new auth token"
    )
    parser.add_argument(
        "--auth-code",
        type=str,
        required=False,
        help="Authorization code for creating a new access token"
    )
    parser.add_argument(
        "--runkeeper-data-path",
        type=str,
        required=True,
        help="Authorization code for creating a new access token"
    )

    args = parser.parse_args()

    strava_client = StravaClient(client_id, client_secret)

    if args.create_access_token:
        if not args.auth_code:
            print("Please provide authorization code to create a new token")
            sys.exit(1)
        strava_client.create_access_token(auth_code=args.auth_code)
        strava_client.save_tokens(config_file)
    else:
        print("Fetching tokens from config file")
        strava_client.get_tokens(config_file)
        strava_client.authenticate()
        strava_client.save_tokens(config_file)

    download_path = args.runkeeper_data_path
    file = 'cardioActivities.csv'

    with zipfile.ZipFile(download_path, 'r') as zip_ref:
        with zip_ref.open(file) as f:
            activities = pd.read_csv(f)
            activities['duration_sec'] = activities['Duration'].apply(time_to_seconds)

            for index,row in activities.iterrows():
                if pd.notna(row['GPX File']):
                    with zip_ref.open(row['GPX File'], 'r') as gpx_file:
                        strava_client.upload_activity(file=gpx_file,
                                                      name=row['Activity Id'],
                                                      description=row['Notes'])
                else:
                    strava_client.create_activity(name=row['Activity Id'],
                                                  description=row['Notes'],
                                                  type='run',
                                                  distance=row['Distance (mi)'] / MILES_PER_METER,
                                                  start_date_local=row['Date'],
                                                  elapsed_time=row['duration_sec'],
                                                  trainer=1)


if __name__ == "__main__":
    main()