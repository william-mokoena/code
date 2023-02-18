import json
import os
from datetime import datetime
from enum import Enum


def allowed_file(filename, ALLOWED_EXTENSIONS):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def make_result(status, data):
    # Creates a standard return object for datastore functions
    return {
        "status": status,
        "data": data
    }


def save_credentials(client_name: str, creator_id: str, credentials):
    if not os.path.exists('./.secrets'):
        os.mkdir('.secrets')

    if (creator_id):
        filepath = f"./.secrets/{creator_id}_{client_name}_credentials.json"

    else:
        filepath = f"./.secrets/{client_name}_credentials.json"

    with open(filepath, "w") as credentials_file:
        json.dump(credentials, fp=credentials_file)


def update_credentials():
    return


def calculate_timelapse(_datetime):
    dt = datetime.strptime(
        _datetime, '%Y-%m-%d %H:%M:%S.%f')
    now = datetime.now()

    hours_passed = (dt.hour-now.hour)
    minutes_passed = (dt.minute-now.minute)
    seconds_passed = (dt.second-now.second)

    timeduration = ((hours_passed*60*60)+(minutes_passed*60)+(seconds_passed))

    return timeduration


class Status(Enum):
    SUCCESSFUL = 1
    UNSUCCESSFUL = 2
    ERROR = 3
