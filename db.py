import uuid
import hashlib

from datetime import datetime

from tinydb import TinyDB, Query
from utils import make_result, Status


class Database:
    def __init__(self, datastorage_path="./"):
        # Creates or opens a datastore if it exists
        storage_path = f"{datastorage_path}/db.json"
        self.db = TinyDB(storage_path)

    def create_user(self, user_credentials):
        # Add a new user document to the datastore
        user = self.db.search(Query().name == user_credentials["name"])

        if len(user) == 0:
            _id = uuid.uuid4()
            new_user = {
                "type": "user",
                "_id": str(_id),
                "name": user_credentials["name"],
                "password": user_credentials["password"]
            }
            user = self.db.insert(new_user)
            return make_result(status=Status.SUCCESSFUL.name, data=user)

    def verify_user(self, user_credentials):
        # Checks supplied user credentials with those in the documents
        User = Query()
        user = self.db.search(User.name == user_credentials["name"])
        if len(user) > 0:
            if user[0]["password"] == user_credentials["password"]:
                return make_result(status=Status.SUCCESSFUL.name, data=user)

            else:
                result = {"message": "Incorrect password"}
                return make_result(status=Status.UNSUCCESSFUL.name, data=result)

        else:
            result = {"message": "Unknown user name"}
            return make_result(status=Status.UNSUCCESSFUL.name, data=result)

    def get_users(self):
        # Gets all user documents
        Users = Query()
        users = self.db.search(Users.type == "user")
        return make_result(status=Status.SUCCESSFUL.name, data=users)

    def get_user(self, user_id):
        # Gets a single user document
        User = Query()
        user = self.db.search(User._id == user_id)

        if len(user) > 0:
            return make_result(status=Status.SUCCESSFUL.name, data=user)

        else:
            result = {"message": "Unknown user ID"}
            return make_result(status=Status.UNSUCCESSFUL.name, data=result)

    def add_subreddit(self, subreddit_name: str, post_requirements, flairs, defaultFlair, verification_required: bool):
        # Add a subreddit document to the datastore
        subreddit = self.db.search(Query().fragment({
            "name": subreddit_name,
            "type": "subreddit"}))

        if (len(subreddit) == 0):
            _id = uuid.uuid4()
            subreddit = self.db.insert({
                "_id": str(_id),
                "type": "subreddit",
                "name": subreddit_name,
                "post_requirements": post_requirements,
                "flairs": flairs,
                "defaultFlair": defaultFlair,
                "verification_required": verification_required
            })
            return make_result(status=Status.SUCCESSFUL.name, data=subreddit)

    def get_subreddits(self):
        # Gets all subreddit documents
        subreddits = self.db.search(Query().fragment({"type": "subreddit"}))
        return make_result(status=Status.SUCCESSFUL.name, data=subreddits)

    def update_subreddit(self, subreddit_id, fields):
        subreddit = self.db.search(Query()._id == subreddit_id)

        if (len(subreddit) > 0):
            data = self.db.update(
                fields=fields,
                doc_ids=[subreddit[0].doc_id]
            )
            return make_result(status=Status.SUCCESSFUL.name, data=data)

    def add_creators(self, creators_data: []):
        # Add a creator document to the datastore
        _id = uuid.uuid4()
        for creator_data in creators_data:
            Creator = Query()
            creator = self.db.search(Creator.cid == creator_data["cid"])

            if len(creator) == 0:
                self.db.insert({
                    "_id": str(_id),
                    "type": "creator",
                    "cid": creator_data["cid"],
                    "fullName": creator_data["full_name"],
                })

    def get_creators(self):
        # Gets all user documents
        Creators = Query()
        creators = self.db.search(Creators.type == "creator")
        return make_result(status=Status.SUCCESSFUL.name, data=creators)

    def create_event(self, created_at, client_name, post_id, status, action, message):
        # Add an event document to the datastore
        event = self.db.search(Query().fragment(
            {
                "type": "event",
                "client": client_name,
                "postId": post_id
            }
        ))

        if (len(event) > 0):
            self.db.remove(doc_ids=[event[0].doc_id])

        _id = uuid.uuid4()
        event = {
            "_id": str(_id),
            "_createdAt": created_at,
            "type": "event",
            "client": client_name,
            "postId": post_id,
            "status": status,
            "action": action,
            "message": message
        }
        event_doc = self.db.insert(event)

        return make_result(status=Status.SUCCESSFUL.name, data=event_doc)

    def get_events(self, client):
        # Gets all event documents
        events = self.db.search(Query().fragment(
            {"type": "event", "client": client}))
        return make_result(status=Status.SUCCESSFUL.name, data=events)

    def add_post(self, post_data):
        # Add a post document to the datastore
        _id = uuid.uuid4()
        hash = hashlib.md5(
            str(post_data["title"]+post_data["media_id"]).encode()).hexdigest()

        Post = Query()
        post = self.db.search(Post.hash == hash)

        if len(post) == 0:
            self.db.insert({
                "_id": str(_id),
                "hash": hash,
                "type": "post",
                "post": post_data,
                "status": "pending",
                "mediaStatus": "remote",
                "nextHandler": "drive"
            })

            # Create an event for the frontend
            self.create_event(
                created_at=str(datetime.now()),
                client_name="sheets",
                post_id=hash,
                status="writen",
                action="pull",
                message="Successfully pulled data regarding post from google sheets")

    def get_posts(self):
        # Gets all post documents
        Posts = Query()
        posts = self.db.search(Posts.type == "post")
        return make_result(status=Status.SUCCESSFUL.name, data=posts)

    def get_post(self, post_id):
        # Get post document
        post = self.db.search(Query()._id == post_id)
        return make_result(status=Status.SUCCESSFUL.name, data=post)

    def update_post(self, post_id, fields):
        post = self.db.search(Query()._id == post_id)

        if (len(post) > 0):
            data = self.db.update(
                fields=fields,
                doc_ids=[post[0].doc_id]
            )
            return make_result(status=Status.SUCCESSFUL.name, data=data)

    def delete_post(self, post_id):
        post = self.db.search(Query()._id == post_id)

        if (len(post) > 0):
            data = self.db.remove(doc_ids=[post[0].doc_id])
            return make_result(status=Status.SUCCESSFUL.name, data=data)

    def imgur_client_details(self, action: str, cid, payload=None):
        def create_details(payload, cid):
            client = self.db.search(Query().fragment({
                "cid": cid,
                "type": "imgur"}))

            if (len(client) == 0):
                # Add a new user document to the datastore
                _id = uuid.uuid4()
                client_data = {
                    "_id": str(_id),
                    "cid": cid,
                    "type": "imgur",
                    "UserLimit": payload["UserLimit"],
                    "UserRemaining": payload["UserRemaining"],
                    "UserReset": payload["UserReset"],
                    "ClientLimit": payload["ClientLimit"],
                    "ClientRemaining": payload["ClientRemaining"]
                }
                data = self.db.insert(client_data)
                return make_result(status=Status.SUCCESSFUL.name, data=data)

            else:
                return make_result(status=Status.SUCCESSFUL.name, data=client[0].doc_id)

        def get_details():
            return

        def update_details(payload, cid):
            data = self.db.update(
                fields=payload["data"],
                doc_ids=[payload["doc_index"]]
            )

            return make_result(status=Status.SUCCESSFUL.name, data=data)

        if (action == "set"):
            return create_details(payload, cid)

        elif (action == "get"):
            return get_details()

        elif (action == "update" and payload != None):
            return update_details(payload, cid)

    def create_schedule(self, client_name: str, submission_id: str, datetime: str):
        # Add a new schedule document to the datastore
        _id = uuid.uuid4()
        schedule_obj = {
            "type": "schedule",
            "_id": str(_id),
            "client": client_name,
            "submission_id": submission_id,
            "datetime": datetime
        }
        schedule_doc = self.db.insert(schedule_obj)

        return make_result(status=Status.SUCCESSFUL.name, data=schedule_doc)

    def get_schedule(self, submission_id: str, client_name: str):
        # Gets all schedule documents meeting the requirements
        schedule_docs = self.db.search(Query().fragment(
            {
                "type": "schedule",
                "submission_id": submission_id,
                "client": client_name
            }
        ))

        return make_result(status=Status.SUCCESSFUL.name, data=schedule_docs)

    def delete_schedule(self, submission_id: str, client_name: str):
        schedule_docs = self.db.search(Query().fragment(
            {
                "type": "schedule",
                "submission_id": submission_id,
                "client": client_name
            }
        ))

        if (len(schedule_docs) > 0):
            data = self.db.remove(doc_ids=[schedule_docs[0].doc_id])
            return make_result(status=Status.SUCCESSFUL.name, data=data)

    def cloutsy_client_details(self, action: str, cid, payload=None):
        """Incomplete"""
        def create_details(payload, cid):
            client = self.db.search(Query().fragment({
                "cid": cid,
                "type": "cloutsy"}))

            if (len(client) == 0):
                _id = uuid.uuid4()
                client_data = {
                    "_id": str(_id),
                    "cid": cid,
                    "type": "cloutsy",
                    "credits": 500
                }
                data = self.db.insert(client_data)
                return make_result(status=Status.SUCCESSFUL.name, data=data)

            else:
                return make_result(status=Status.SUCCESSFUL.name, data=client[0].doc_id)

        def get_details():
            return

        def update_details(payload, cid):
            data = self.db.update(
                fields=payload["data"],
                doc_ids=[payload["doc_index"]]
            )

            return make_result(status=Status.SUCCESSFUL.name, data=data)

        if (action == "set"):
            return create_details(payload, cid)

        elif (action == "get"):
            return get_details()

        elif (action == "update" and payload != None):
            return update_details(payload, cid)

    def create_submission(self, payload):
        _id = uuid.uuid4()
        hash = hashlib.md5(
            str(payload["title"]+payload["img_link"]).encode()).hexdigest()

        submission_doc = self.db.search(Query().fragment({
            "hash": hash,
            "type": "submission"}))

        if (len(submission_doc) == 0):
            submission_obj = {
                "type": "submission",
                "_id": str(_id),
                "hash": hash,
                "cid": payload["cid"],
                "postId": payload["post_id"],
                "subreddit_name": payload["subreddit_name"],
                "title": payload["title"],
                "img_link": payload["img_link"],
                "flair_id": payload["flair_id"],
                "approved": payload["approved"]
            }
            submission_doc = self.db.insert(submission_obj)

            return make_result(status=Status.SUCCESSFUL.name, data=submission_doc)

    def get_all_submissions(self):
        submissions = self.db.search(Query().fragment(
            {"type": "submission"}))

        return make_result(status=Status.SUCCESSFUL.name, data=submissions)

    def get_submissions(self, post_id: str):
        submissions = self.db.search(Query().fragment(
            {
                "type": "submission",
                "post_id": post_id
            }
        ))

        return make_result(status=Status.SUCCESSFUL.name, data=submissions)

    def update_submission(self, submission_id, fields):
        submission = self.db.search(Query()._id == submission_id)

        if (len(submission) > 0):
            data = self.db.update(
                fields=fields,
                doc_ids=[submission[0].doc_id]
            )
            return make_result(status=Status.SUCCESSFUL.name, data=data)

    def delete_submission(self, submission_id):
        submission = self.db.search(Query()._id == submission_id)

        if (len(submission) > 0):
            data = self.db.remove(doc_ids=[submission[0].doc_id])
            return make_result(status=Status.SUCCESSFUL.name, data=data)
