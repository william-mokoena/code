import json
from os import path
from imgur_python import Imgur

STATE = 63870


def get_imgur_oauth_url(client_id: str,
                        client_secret: str,
                        account_username: str):

    imgur_client = Imgur({
        "client_id": client_id,
        "client_secret": client_secret,
        "account_username": account_username
    })

    auth_url = imgur_client.authorize()
    return auth_url


def get_credentials(cid: str):
    with open(f"./.secrets/{cid}_imgur_credentials.json", "r") as _file:
        credentials = json.load(_file)

    return credentials


def upload(credentials, img_filepath: str):
    imgur_client = Imgur(credentials)
    response = imgur_client.image_upload(
        filename=img_filepath,
        title=None,
        description=None,
        album=None,
        disable_audio=0
    )

    return response
