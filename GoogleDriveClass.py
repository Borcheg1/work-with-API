import io

import requests

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive


class Google:
    def __init__(self):
        self.gauth = GoogleAuth()
        self.gauth.LocalWebserverAuth()
        self.drive = GoogleDrive(self.gauth)

    def create_folder(self, folder_name):
        self.folder_name = folder_name
        folder = self.drive.CreateFile({
            'title': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        })
        folder.Upload()
        return folder['id']

    def upload_file(self, folder_id, url, file_name):
        post_url = "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart"
        headers = {
            "Authorization": "Bearer " + self.gauth.credentials.access_token
        }
        metadata = {
            'name': file_name,
            'parents': [folder_id]
        }
        files = {
            'data': ('metadata', str(metadata), 'application/json'),
            'file': io.BytesIO(requests.get(url).content)
        }
        response = requests.post(post_url, headers=headers, files=files)
        return response
