import socket
import sys
import json
import time
from datetime import datetime

import praw
import prawcore
import requests

from db import Database
from utils import calculate_timelapse

STATE = 63876

database = Database()


def get_credentials(cid: str):
    filpath = f"./.secrets/{cid}_reddit_credentials.json"
    with open(filpath, 'r') as fp:
        credentials = json.load(fp)

    return credentials


def get_reddit_oauth_url(client_id: str, client_secret: str, redirect_uri: str, user_agent: str, username: str, proxies):
    session = requests.Session()
    session.proxies.update(proxies)

    scopes = ["*"]

    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        user_agent=f'{user_agent} by u/{username}',
        username=username
    )
    url = reddit.auth.url(duration="permanent", scopes=scopes, state=STATE)

    return url


def get_reddit_refresh_token(client_id: str, client_secret: str, redirect_uri: str, user_agent: str, username: str, code: int, proxies):
    session = requests.Session()
    session.proxies.update(proxies)

    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        user_agent=f'{user_agent} by u/{username}',
        username=username
    )
    refresh_token = reddit.auth.authorize(code)

    return refresh_token


def make_post(cid: str, subreddit_name: str, title: str, img_link: str, flair_id: str):
    CREDENTIALS = get_credentials(cid=cid)
    proxies = CREDENTIALS["proxies"]
    session = requests.Session()
    session.proxies.update(proxies)

    reddit = praw.Reddit(
        client_id=CREDENTIALS["client_id"],
        client_secret=CREDENTIALS["client_secret"],
        user_agent=f'{CREDENTIALS["user_agent"]} by u/{CREDENTIALS["username"]}',
        redirect_uri=CREDENTIALS["redirect_uri"],
        refresh_token=CREDENTIALS["refresh_token"],
        # requestor_kwargs={"session": session}
    )

    subreddit = reddit.subreddit(display_name=subreddit_name)
    submission = subreddit.submit(title=title, url=img_link, flair_id=flair_id)

    return submission


def get_subreddit_attributes(subreddit_name: str):
    CREDENTIALS = get_credentials(cid="admin")
    reddit = praw.Reddit(
        client_id=CREDENTIALS["client_id"],
        client_secret=CREDENTIALS["client_secret"],
        user_agent=f'{CREDENTIALS["user_agent"]} by u/{CREDENTIALS["username"]}',
        username=CREDENTIALS["username"],
        redirect_uri=CREDENTIALS["redirect_uri"],
        refresh_token=CREDENTIALS["refresh_token"]
    )

    subreddit = reddit.subreddit(display_name=subreddit_name)

    post_requirements = subreddit.post_requirements()

    try:
        flairs = [*subreddit.flair.link_templates]

    except prawcore.exceptions.Forbidden:
        flairs = []

    return {"post_requirements": post_requirements, "flairs": flairs}


def duration_from_last_post(cid: str):
    '''Returns the time lapse between the current time and the time a client last posted in seconds'''
    events = database.get_events('reddit')['data']
    posts = database.get_posts()['data']
    if (len(events) > 0):
        for event in events:
            if (event['client'] == 'reddit'):
                post_id = event['postId']

                for post in posts:
                    if (post['_id'] == post_id and post['post']['cid'] == cid):
                        event_timestamp = event['_createdAt']
                        duration = calculate_timelapse(event_timestamp)
                        return duration

    else:
        return None
