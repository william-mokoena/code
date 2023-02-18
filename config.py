import os
import json


CLIENT_NAMES = {
    "GOOGLE": "google_service_account_credentials.json",
    "IMGUR": "imgur_credentials.json",
    "REDDIT": "reddit_credentials.json"
}


def get_credentials_filepath(client_name):
    return os.path.realpath(".secrets/"+CLIENT_NAMES[client_name])


def get_credentials(client_name):
    credentials_filepath = get_credentials_filepath(client_name)
    with open(credentials_filepath, "r") as credentials:
        creds = json.load(credentials)

    return creds


def set_refresh_token(client_name, refresh_token):
    credentials_filepath = get_credentials_filepath(client_name)

    with open(credentials_filepath, "r") as credentials_file:
        creds = json.load(credentials_file)

    creds["refresh_token"]=refresh_token

    with open(credentials_filepath, "w") as credentials_file:
        json.dump(obj=creds,fp=credentials_file, indent=2)

    return
