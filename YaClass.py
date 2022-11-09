import requests


class Ya:
    def __init__(self, auth_token):
        self.auth_token = auth_token
        self.headers = {
            'content-type': 'application/json',
            'authorization': f'OAuth {self.auth_token}'
        }

    def upload_file(self, download_url, name, folder_name):
        main_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        params = {
            'path': fr'{folder_name}/{name}',
            'url': download_url,
            'disable_redirects': True
        }
        response = requests.post(main_url, headers=self.headers, params=params)
        return response

    def create_folder(self, user_id, folder_name):
        main_url = 'https://cloud-api.yandex.net/v1/disk/resources'
        params = {'path': folder_name}
        response = requests.put(main_url, headers=self.headers, params=params)
        if response.status_code != 201:
            raise Exception(f'{response.json()["error"]}')
        return folder_name
