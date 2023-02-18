import io
import os

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account

DRIVE_SCOPES = ["https://www.googleapis.com/auth/drive"]
SHEETS_SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
GOOGLE_CREDENTIALS_FILE = "./.secrets/google_service_account_credentials.json"


def initialize_drive_client():
    """Initializes an drive service object.

    Returns:
      An authorized drive service object.
    """
    credentials = service_account.Credentials.from_service_account_file(
        GOOGLE_CREDENTIALS_FILE, scopes=DRIVE_SCOPES)

    # Build the service object.
    service = build("drive", "v3", credentials=credentials)

    return service


def initialize_sheets_client():
    """Initializes an sheets service object.

    Returns:
      An authorized sheets service object.
    """
    credentials = service_account.Credentials.from_service_account_file(
        GOOGLE_CREDENTIALS_FILE, scopes=SHEETS_SCOPES)

    # Build the service object.
    service = build("sheets", "v4", credentials=credentials)

    return service


def download_content(drive_service, file_id: str):
    request = drive_service.files().get_media(
        fileId=file_id)
    drive_file = drive_service.files().get(fileId=file_id).execute()

    mime_type = drive_file['mimeType']

    if not os.path.exists('media'):
        os.mkdir('media')
        if not os.path.exists('media/pending'):
            os.mkdir('media/pending')

    fh = io.FileIO(f"./media/pending/{file_id}.{mime_type.split('/')[1]}", mode="wb")
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        return fh
