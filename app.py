import os
import shutil
import json
import time
from datetime import datetime, timedelta
import requests
import schedule
import uuid

from flask import (
    Flask,
    request,
    url_for,
    jsonify,
    redirect,
    request,
    current_app,
    flash
)
from flask_cors import CORS
from flask_apscheduler import APScheduler

from functools import wraps
import jwt
from werkzeug.utils import secure_filename

from db import Database
from utils import (
    allowed_file,
    calculate_timelapse,
    make_result,
    Status,
    save_credentials
)


from google_client import initialize_sheets_client
from reddit_client import (
    get_reddit_oauth_url,
    get_subreddit_attributes,
    get_reddit_refresh_token
)
from imgur_client import get_imgur_oauth_url

import google_client
import imgur_client
import reddit_client
import cloutsy_client

from db import Database

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'premiercreators-secret'
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
app.config['ALLOWED_EXTENSIONS'] = {"json"}

CORS(app)

# initialize scheduler
scheduler = APScheduler()
scheduler.api_enabled = True
scheduler.init_app(app)

database = Database()

CONTENT_DATA_RANGE = 'content!A1:E20'


@scheduler.task('interval', id='request_post_data_from_sheets', minutes=15, misfire_grace_time=900)
def request_post_data_from_sheets():
    print('[INFO] Requesting google sheets data...')
    creators_query = database.get_creators()
    creators_data = creators_query['data']

    try:
        sheets_service = google_client.initialize_sheets_client()

        # Iterate through creators_data
        for creator_data in creators_data:
            # Get content data from spread sheet
            api_request = sheets_service.spreadsheets().values().get(
                spreadsheetId=creator_data['cid'], range=CONTENT_DATA_RANGE)
            api_response = api_request.execute()
            table_values = api_response['values']

            table_cols = table_values[0]
            table_post_rows = table_values[1:]

            # Create a post documents from content data
            for index, post_row in enumerate(table_post_rows):
                _id = uuid.uuid4()
                single_post = {
                    'cid': creator_data['cid']
                }
                for index, col in enumerate(table_cols):
                    single_post[col] = post_row[index]

                database.add_post(post_data=single_post)

        return 0

    except FileNotFoundError:
        pass


@scheduler.task('interval', id='download_content_data_drive', minutes=20, misfire_grace_time=900)
def download_content_data_drive():
    print('[INFO] Downloading media from google drive...')
    posts_query = database.get_posts()
    posts_data = posts_query['data']

    try:
        drive_service = google_client.initialize_drive_client()

        for post_data in posts_data:
            if (post_data['mediaStatus'] == 'remote'):
                file_id = post_data['post']['media_id']
                google_client.download_content(drive_service, file_id)

                database.update_post(
                    post_id=post_data['_id'],
                    fields={
                        "mediaStatus": "local",
                        "nextHandler": "imgur"
                    })
                # Create an event for the frontend
                database.create_event(
                    created_at=str(datetime.now()),
                    client_name='drive',
                    post_id=post_data['_id'],
                    status='saved',
                    action='download',
                    message='Successfully downloaded media for post from google drive')

        return 0

    except FileNotFoundError:
        pass


@scheduler.task('interval', id='upload_to_imgur', minutes=30, misfire_grace_time=900)
def upload_to_imgur():
    print('[INFO] Uploading to imgur...')

    def get_rate_credits(cid):
        url = "https://api.imgur.com/3/credits"
        headers = {
            'Authorization': f'Bearer {client_credentials["access_token"]}'
        }

        response = requests.request("GET", url, headers=headers)

        return response.json()["data"]

    # Open media/pending
    # We are permitted approximately 1,250 uploads per day
    posts = database.get_posts()['data']

    try:
        for post in posts:
            status = post['status']
            handler = post['nextHandler']
            media_id = post['post']['media_id']
            cid = post['post']['cid']

            client_credentials = imgur_client.get_credentials(cid=cid)
            rate_credits = get_rate_credits(cid)
            result = database.imgur_client_details(
                action="set", payload=rate_credits, cid=cid)
            doc_index = result['data']

            if (handler == 'imgur' and status == 'pending'):
                img_filepath = ''
                imgur_links = []
                files_pending = os.listdir('media/pending')

                for media_file in files_pending:
                    if (media_file.split('.')[0] == media_id):
                        img_filepath = os.path.realpath(
                            f'./media/pending/{media_file}')

                try:
                    for num_links in range(0, 3):
                        if (rate_credits["ClientRemaining"] > 10):
                            response = imgur_client.upload(credentials=client_credentials,
                                                           img_filepath=img_filepath)

                            img_link = response['response']['data']['link']
                            rate_credits = get_rate_credits(cid)
                            update_payload = {
                                'data': rate_credits,
                                'doc_index': doc_index
                            }
                            database.imgur_client_details(
                                action="update",
                                payload=update_payload,
                                cid=cid
                            )
                            imgur_links.append(img_link)
                            time.sleep(2)

                        else:
                            raise Exception(
                                "Not enough credits. Try again tomorrow.")

                    if not os.path.exists('./media/uploaded'):
                        os.mkdir('./media/uploaded')
                        shutil.move(src=img_filepath,
                                    dst=f'./media/uploaded/{media_file}')

                except Exception as exception:
                    print(exception)

                database.update_post(
                    post_id=post['_id'],
                    fields={
                        "nextHandler": "reddit",
                        "mediaLinks": imgur_links
                    })

                database.create_event(
                    created_at=str(datetime.now()),
                    client_name='imgur',
                    post_id=post['_id'],
                    status='uploaded',
                    action='post',
                    message='Successfully posted media for post to imgur')

        return 0

    except FileNotFoundError:
        pass


@scheduler.task('interval', id='create_submission_documents', minutes=7, misfire_grace_time=900)
def create_submission_documents():
    # print("[INFO] Creating submission documents...")
    subreddits = database.get_subreddits()["data"]
    posts = database.get_posts()["data"]

    if (len(subreddits) > 0 and len(posts) > 0):
        for post in posts:

            if (post["nextHandler"] != "reddit"):
                continue

            if (len(post["mediaLinks"]) > 0):
                try:
                    for index in range(0, len(post["mediaLinks"])+1):
                        submission_obj = {
                            "cid": post["post"]["cid"],
                            "subreddit_name": subreddits[index]["name"],
                            "title": post["post"]["title"],
                            "img_link": post["mediaLinks"][index],
                            "flair_id": None,
                            "approved": False,
                            "post_id": post["_id"]
                        }

                        database.create_submission(submission_obj)

                except IndexError:
                    continue

    return 0


@scheduler.task('interval', id='schedule_submissions_for_posting', minutes=7, misfire_grace_time=900)
def schedule_submissions_for_posting():
    print("[INFO] Creating schedules for posting...")
    submission_docs = database.get_all_submissions()["data"]

    try:
        for submission_doc in submission_docs:
            if (not submission_doc["approved"]):
                continue

            # Try to find a schedule for this submission
            current_schedule = database.get_schedule(
                submission_doc['_id'], 'reddit'
            )['data']

            if (len(current_schedule) == 0):
                # [info] No schedule for the submission was found so we create itprecious gift matlala

                # Use the 'cid' to find the last time the client was used to make a reddit submission
                duration_since_last_post = reddit_client.duration_from_last_post(
                    submission_doc["cid"])

                if (not duration_since_last_post):
                    database.create_schedule(
                        client_name="reddit",
                        submission_id=submission_doc["_id"],
                        datetime=str(datetime.now())
                    )

                else:
                    # Use 'duration_since_last_post' to calculate the time we can make a reddit submission
                    datetime_to_post = datetime.now()+timedelta(seconds=((duration_since_last_post-900)*-1))

                    database.create_schedule(
                        client_name="reddit",
                        submission_id=submission_doc["_id"],
                        datetime=str(datetime_to_post)
                    )

        return 0

    except FileNotFoundError:
        pass


@scheduler.task('interval', id='post_on_reddit', minutes=4, misfire_grace_time=900)
def post_on_reddit():
    def cleanup():
        # delete submission document after post is made to reddit
        database.delete_submission(submission_id=submission_doc["_id"])
        database.delete_schedule(
            submission_id=submission_doc["_id"],
            client_name="reddit")

        post = database.get_post(
            post_id=submission_doc["postId"])["data"][0]

        if (post):

            try:
                '''
                [BUGS]
                1. List elements are not being appended individually
                2. nextHandler is updated to "cloutsy" even though not all submissions for
                post have been made
                3. Posts are being made way too frequently
                '''
                reddit_posts_ids = []
                subreddits_names = []

                reddit_posts_ids.extend(post["redditPosts"]["ids"])
                reddit_posts_ids.append(reddit_submission.id)

                subreddits_names .extend(post["redditPosts"]["subreddits"])
                subreddits_names.append(submission_doc["subreddit_name"])

                # Check it we have any more submissions to make
                # if not then we change 'nextHandler' to 'cloutsy'

                corr_submission_docs = database.get_submissions(post_id=post["_id"])[
                    "data"]

                if (len(corr_submission_docs) == 0):
                    database.update_post(
                        post_id=submission_doc["postId"],
                        fields={
                            "nextHandler": "cloutsy",
                            "redditPosts": {
                                "subreddits": subreddits_names,
                                "ids": reddit_posts_ids
                            }
                        })

                else:
                    database.update_post(
                        post_id=submission_doc["postId"],
                        fields={
                            "redditPosts": {
                                "subreddits": subreddits_names,
                                "ids": reddit_posts_ids
                            }
                        })

            except KeyError as key_error:
                database.update_post(
                    post_id=submission_doc["postId"],
                    fields={
                        "redditPosts": {
                            "subreddits": [submission_doc["subreddit_name"]],
                            "ids": [reddit_submission.id]
                        }
                    })

            database.create_event(
                created_at=str(datetime.now()),
                client_name='reddit',
                post_id=submission_doc["postId"],
                status='posted',
                action='post',
                message='Successfully posted to reddit')

    # Find the number of submissions that correspond to a post
    submission_docs = database.get_all_submissions()["data"]

    try:
        for submission_doc in submission_docs:
            # Schedule all the submissions according to the clients
            # Each client only gets to make 1 post every 15-16 minutes

            # Make those submissions to reddit and append each reddit link to the submission
            # to it's responding posts redditPosts field and delete the submission
            # After all submissions have been made update the post nextHandler to cloutsy
            if (not submission_doc["approved"]):
                continue

            # Find schedule for the submission and schedule
            posting_schedule = database.get_schedule(
                submission_id=submission_doc["_id"],
                client_name="reddit"
            )["data"]

            if (len(posting_schedule) == 0):
                continue

            # how many seconds left until we can post
            duration_to_make_post = calculate_timelapse(
                posting_schedule[0]['datetime'])

            # how many seconds since we last posted
            duration_since_last_post = reddit_client.duration_from_last_post(
                cid=submission_doc["cid"])

            if (not duration_since_last_post):
                print("[INFO] Posting to reddit...")
                reddit_submission = reddit_client.make_post(
                    cid=submission_doc["cid"],
                    subreddit_name=submission_doc["subreddit_name"],
                    title=submission_doc["title"],
                    img_link=submission_doc["img_link"],
                    flair_id=submission_doc["flair_id"]
                )
                cleanup()

            elif (duration_since_last_post < -900 and duration_to_make_post <= 0):
                print("[INFO] Posting to reddit...")
                reddit_submission = reddit_client.make_post(
                    cid=submission_doc["cid"],
                    subreddit_name=submission_doc["subreddit_name"],
                    title=submission_doc["title"],
                    img_link=submission_doc["img_link"],
                    flair_id=submission_doc["flair_id"]
                )
                cleanup()

        return 0

    except FileNotFoundError:
        pass


@scheduler.task('interval', id='add_orders_to_cloutsy', minutes=20, misfire_grace_time=900)
def add_orders_to_cloutsy():
    posts = database.get_posts()['data']

    try:
        for post in posts:
            cid = post['post']['cid']
            title = post['post']['title']
            post_id = post['_id']
            handler = post['nextHandler']

            if (handler == 'cloutsy'):
                reddit_posts = post['redditPosts']
                subreddits = reddit_posts['subreddits']
                post_ids = reddit_posts['ids']

                print("[INFO] Adding order to cloutsy...")
                for index, subreddit in enumerate(subreddits):
                    post_id = post_ids[index]
                    url = f'https://www.reddit.com/r/{subreddit}/comments/{post_id}'
                    response = cloutsy_client.add_order(url)

                    if ('error' in response.json().keys()):
                        print(
                            f"[ERROR] CLIENT:CLOUTSY - {response.json()['error']}")
                        continue

                    database.update_post(
                        post_id=post_id,
                        fields={
                            "nextHandler": None
                        })

                    database.create_event(
                        created_at=str(datetime.now()),
                        client_name='cloutsy',
                        post_id=post_id,
                        status='added',
                        action='order',
                        message='Successfully added order to cloutsy')

        return 0

    except FileNotFoundError:
        pass

# @scheduler.task('interval', id='clear_cached_content', seconds=30, misfire_grace_time=900)


def clear_cached_content():
    return 0


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]
        if not token:
            return {
                "message": "Authentication Token is missing!",
                "data": None,
                "error": "Unauthorized"
            }, 401
        try:
            data = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
            current_user = database.get_user(data["user_id"])
            if current_user is None:
                return {
                    "message": "Invalid Authentication token!",
                    "data": None,
                    "error": "Unauthorized"
                }, 401
        except Exception as e:
            return {
                "message": "Something went wrong",
                "data": None,
                "error": str(e)
            }, 500

        return f(current_user, *args, **kwargs)

    return decorated


@app.post("/login")
def login():
    request_data = request.get_json()
    result = database.verify_user(request_data)
    if result["status"] == Status.UNSUCCESSFUL.name:
        return jsonify(result)

    elif result["status"] == Status.SUCCESSFUL.name:
        if len(result["data"]) > 0:
            user = result["data"][0]
            try:
                # token should expire after 24 hrs
                user["token"] = jwt.encode(
                    {"user_id": user["_id"]},
                    app.config["SECRET_KEY"],
                    algorithm="HS256"
                )
                return {
                    "status": Status.SUCCESSFUL.name,
                    "data": user
                }
            except Exception as e:
                return {
                    "error": "Something went wrong",
                    "message": str(e)
                }, 500


@app.post("/signup")
def signup():
    request_data = request.get_json()
    result = database.create_user(request_data)
    return jsonify(result)


GOOGLE_CREDENTIALS_FILENAME = "google_service_account_credentials.json"


@app.post("/api/client/google/upload_credentials")
@token_required
def upload_credentials(current_user):
    ALLOWED_EXTENSIONS = app.config['ALLOWED_EXTENSIONS']
    UPLOAD_FOLDER = app.config['UPLOAD_FOLDER']

    # check if the post request has the file part
    if 'file' not in request.files:
        return make_result(
            status=Status.UNSUCCESSFUL.name,
            data={
                "message": "No file part"
            }
        )

    file = request.files['file']

    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == '':
        return make_result(
            status=Status.UNSUCCESSFUL.name,
            data={
                "message": "File is missing"
            }
        )

    if not allowed_file(file.filename, ALLOWED_EXTENSIONS):
        file.save(os.path.join(
            UPLOAD_FOLDER, GOOGLE_CREDENTIALS_FILENAME))

        return make_result(
            status=Status.UNSUCCESSFUL.name,
            data={
                "message": "File type is not allowed"
            }
        )

    if file and allowed_file(file.filename, ALLOWED_EXTENSIONS):
        if not os.path.exists(UPLOAD_FOLDER):
            os.mkdir(UPLOAD_FOLDER)

        file.save(os.path.join(
            UPLOAD_FOLDER, GOOGLE_CREDENTIALS_FILENAME))

        return make_result(
            status=Status.SUCCESSFUL.name,
            data={
                "message": "Credentials file uploaded"
            }
        )


@app.get("/api/client/google/init_google_client")
@token_required
def init_google_client(current_user):
    if ".secrets" not in os.listdir('./'):
        os.mkdir(".secrets")

    shutil.copy(f"./uploads/{GOOGLE_CREDENTIALS_FILENAME}", ".secrets")

    return make_result(status=Status.SUCCESSFUL.name, data={"state": "initialized"})


@app.get("/api/client/google/google_client_state")
@token_required
def google_client_state(current_user):
    if os.path.exists(f"./uploads/{GOOGLE_CREDENTIALS_FILENAME}"):
        return make_result(status=Status.SUCCESSFUL.name, data={"state": "active"})

    if not os.path.exists(f"./uploads/{GOOGLE_CREDENTIALS_FILENAME}"):
        return make_result(status=Status.SUCCESSFUL.name, data={"state": "not-active"})


@app.post("/api/get_creators")
@token_required
def get_creators(current_user):
    request_data = request.get_json()
    SPREADSHEET_ID = request_data['sheetId']
    CREATOR_ID_NAME_RANGE = request_data['dataRange']

    try:
        # Init sheets client
        sheets_service = initialize_sheets_client()

        # # Open up creators sheet
        api_request = sheets_service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID, range=CREATOR_ID_NAME_RANGE)

        api_response = api_request.execute()
        table_values = api_response['values']

        resp_data = []
        _keys = table_values[0]
        _values = table_values[1:]

        for value in _values:
            resp_data.append({
                _keys[0]: value[0],
                _keys[1]: value[1]
            })

        database.add_creators(creators_data=resp_data)

        return make_result(status=Status.SUCCESSFUL.name, data=resp_data)

    except Exception as exception:
        print(exception)
        return make_result(status=Status.UNSUCCESSFUL.name, data="")


@app.get("/api/foreign_get_credentials/<cid>")
@token_required
def get_creator_credentials(current_user, cid):
    # Init sheets client
    sheets_service = initialize_sheets_client()

    # # Open up creators sheet
    api_request = sheets_service.spreadsheets().values().get(
        spreadsheetId=cid, range='credentials!A1:C5')

    api_response = api_request.execute()
    table_values = api_response['values']

    services = table_values[0][1:]
    _values = table_values[1:]

    reddit_client_id = table_values[1][1]
    reddit_client_secret = table_values[2][1]
    reddit_username = table_values[3][1]
    reddit_password = table_values[4][1]

    imgur_client_id = table_values[1][2]
    imgur_client_secret = table_values[2][2]
    imgur_username = table_values[3][2]
    imgur_password = table_values[4][2]

    resp_data = {
        'reddit': {
            'client_id': reddit_client_id,
            'client_secret': reddit_client_secret,
            'username': reddit_username,
            'password': reddit_password
        },
        'imgur': {
            'client_id': imgur_client_id,
            'client_secret': imgur_client_secret,
            'username': imgur_username,
            'password': imgur_password
        }
    }

    return make_result(status=Status.SUCCESSFUL.name, data=resp_data)


@app.post("/api/client/reddit/set_reddit_credentials")
@token_required
def set_reddit_credentials(current_user):
    request_data = request.get_json()
    url = get_reddit_oauth_url(
        client_id=request_data["clientId"],
        client_secret=request_data["clientSecret"],
        redirect_uri=request_data["redirectUri"],
        user_agent=request_data["userAgent"],
        proxies=request_data["proxies"],
        username=request_data["username"])

    return make_result(status=Status.SUCCESSFUL.name, data={"url": url})


@app.post("/api/client/reddit/set_reddit_refresh_token")
@token_required
def set_reddit_refresh_token(current_user):
    request_data = request.get_json()
    refresh_token = get_reddit_refresh_token(
        client_id=request_data["clientId"],
        client_secret=request_data["clientSecret"],
        redirect_uri=request_data["redirectUri"],
        user_agent=request_data["userAgent"],
        username=request_data["username"],
        proxies=request_data["proxies"],
        code=request_data["authorizationCode"])

    credentials = {
        "client_id": request_data["clientId"],
        "client_secret": request_data["clientSecret"],
        "redirect_uri": request_data["redirectUri"],
        "user_agent": request_data["userAgent"],
        "username": request_data["username"],
        "proxies": request_data["proxies"],
        "refresh_token": refresh_token,
    }

    save_credentials(
        client_name="reddit",
        creator_id=request_data["_cid"],
        credentials=credentials)

    return make_result(status=Status.SUCCESSFUL.name, data="")


@app.get("/api/client/reddit/reddit_client_state/<cid>")
@token_required
def reddit_client_state(current_user, cid):
    if os.path.exists(f"./.secrets/{cid}_reddit_credentials.json"):
        return make_result(status=Status.SUCCESSFUL.name, data={"state": "active"})

    if not os.path.exists(f"./.secrets/{cid}_reddit_credentials.json"):
        return make_result(status=Status.SUCCESSFUL.name, data={"state": "not-active"})


@app.post("/api/client/imgur/set_imgur_credentials")
@token_required
def set_imgur_credentials(current_user):
    request_data = request.get_json()
    url = get_imgur_oauth_url(
        client_id=request_data["clientId"],
        client_secret=request_data["clientSecret"],
        account_username=request_data["accountUsername"])

    return make_result(status=Status.SUCCESSFUL.name, data={"url": url})


@app.post("/api/client/imgur/set_imgur_refresh_token")
@token_required
def set_imgur_refresh_token(current_user):
    request_data = request.get_json()
    credentials = {
        "client_id": request_data["clientId"],
        "client_secret": request_data["clientSecret"],
        "account_username": request_data["accountUsername"],
        "access_token": request_data["accessToken"],
        "token_type": "bearer",
        "expires_in": request_data["expiresIn"],
        "refresh_token": request_data["refreshToken"],
    }

    save_credentials(client_name="imgur",
                     creator_id=request_data["_cid"],  credentials=credentials)

    return make_result(status=Status.SUCCESSFUL.name, data="")


@app.get("/api/client/imgur/imgur_client_state/<cid>")
@token_required
def imgur_client_state(current_user, cid):
    if os.path.exists(f"./.secrets/{cid}_imgur_credentials.json"):
        return make_result(status=Status.SUCCESSFUL.name, data={"state": "active"})

    if not os.path.exists(f"./.secrets/{cid}_imgur_credentials.json"):
        return make_result(status=Status.SUCCESSFUL.name, data={"state": "not-active"})


@app.post("/api/client/cloutsy/set_cloutsy_credentials")
@token_required
def set_cloutsy_credentials(current_user):
    request_data = request.get_json()
    credentials = {
        "api_key": request_data["apiKey"]
    }
    save_credentials(client_name="cloutsy",
                     creator_id=None,  credentials=credentials)

    return make_result(status=Status.SUCCESSFUL.name, data="")


@app.get("/api/client/cloutsy/cloutsy_client_state")
@token_required
def cloutsy_client_state(current_user):
    if os.path.exists(f"./.secrets/cloutsy_credentials.json"):
        return make_result(status=Status.SUCCESSFUL.name, data={"state": "active"})

    if not os.path.exists(f"./.secrets/cloutsy_credentials.json"):
        return make_result(status=Status.SUCCESSFUL.name, data={"state": "not-active"})


@app.get("/api/add_subreddit")
@token_required
def add_subreddit(current_user):
    subreddit_name = request.args.get('name', default='reddit', type=str)
    _verification_required = request.args.get(
        'verificationRequired', default='false', type=str)

    if _verification_required == "true":
        verification_required = True

    else:
        verification_required = False

    subreddit_attributes = get_subreddit_attributes(
        subreddit_name=subreddit_name
    )

    if (len(subreddit_attributes["flairs"]) > 0):
        defaultFlair = subreddit_attributes["flairs"][0]

    else:
        defaultFlair = None

    subreddit_doc = database.add_subreddit(subreddit_name=subreddit_name,
                                           post_requirements=subreddit_attributes["post_requirements"],
                                           flairs=subreddit_attributes["flairs"],
                                           defaultFlair=defaultFlair,
                                           verification_required=verification_required)

    return make_result(status=Status.SUCCESSFUL.name, data=subreddit_doc)


@app.get("/api/subreddits")
@token_required
def subreddits(current_user):
    subreddit_docs = database.get_subreddits()["data"]

    return make_result(status=Status.SUCCESSFUL.name, data=subreddit_docs)


@app.patch("/api/update_subreddit")
@token_required
def update_subreddit(current_user):
    request_data = request.get_json()
    res = database.update_subreddit(
        subreddit_id=request_data["_id"],
        fields=request_data["fields"]
    )["data"]

    return make_result(status=Status.SUCCESSFUL.name, data="")


@app.get("/api/events")
@token_required
def events(current_user):
    client = request.args.get('client', default='reddit', type=str)
    events = database.get_events(client)["data"]

    return make_result(status=Status.SUCCESSFUL.name, data=events)


@app.get("/api/post")
@token_required
def post(current_user):
    post_id = request.args.get('id', type=str)
    post = database.get_post(post_id)

    return make_result(status=Status.SUCCESSFUL.name, data=post)


@app.delete("/api/delete_post")
@token_required
def delete_post(current_user):
    post_id = request.args.get('id', type=str)
    deleted_post = database.delete_post(post_id)

    return make_result(status=Status.SUCCESSFUL.name, data=deleted_post)


@app.get("/api/posts")
@token_required
def posts(current_user):
    posts = database.get_posts()["data"]
    make_result(status=Status.SUCCESSFUL.name, data=posts)

    return make_result(status=Status.SUCCESSFUL.name, data=posts)


@app.get("/api/submissions")
@token_required
def submissions(current_user):
    submission_docs = database.get_all_submissions()["data"]

    return make_result(status=Status.SUCCESSFUL.name, data=submission_docs)


@app.patch("/api/update_submission")
@token_required
def update_submission(current_user):
    request_data = request.get_json()
    res = database.update_submission(
        submission_id=request_data["_id"],
        fields=request_data["fields"]
    )["data"]

    return make_result(status=Status.SUCCESSFUL.name, data=res)


def startup():
    scheduler.start()

    admin_user_credentials = {
        "name": "admin",
        "password": "admin@premiercreators"
    }

    database.create_user(user_credentials=admin_user_credentials)


startup()
