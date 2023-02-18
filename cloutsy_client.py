import json
import requests


def add_order(reddit_post_url: str):
    with open("./.secrets/cloutsy_credentials.json", "r") as fp:
        credentials = json.load(fp)

    api_key = credentials["api_key"]

    url = f'https://cloutsy.com/api/v2?key={api_key}&action=add&service=1534&link={reddit_post_url}&quantity=100'
    response = requests.request("GET", url)
    return response
