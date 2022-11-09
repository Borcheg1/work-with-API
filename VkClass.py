import requests
import json
import time
from datetime import datetime


class Vk:
    def __init__(self, auth_token: str):
        self.auth_token = auth_token
        self.params = {
            'access_token': auth_token,
            'v': '5.131'
        }

    def get_photos_url(self, user_id, album) -> list:
        photo_count = int(input(f'У пользователя {album[1]} фотографий. '
                                f'Сколько фотографий скачать? Введите число:\n'))
        url = 'https://api.vk.com/method/photos.get'
        params = {
            'owner_id': user_id,
            'album_id': album[0],
            'rev': 0,
            'extended': 1,
            'photo_size': 1,
            'count': photo_count,
            'offset': 0
        }

        self._create_new_json_file()

        if photo_count > album[1]:
            offset = album[1]
        else:
            offset = photo_count
        if photo_count > 1000 and album[1] > 1000:
            params['count'] = 1000

        list_with_info = []
        list_with_url = []

        while params['offset'] < offset:
            response = requests.get(url, params={**self.params, **params}).json()
            self._check_error(response)
            self._get_info_from_response(response, list_with_info, list_with_url)
            params['offset'] += 1000
            if offset - params['offset'] < 1000:
                params['count'] = offset - params['offset']
            time.sleep(0.5)
        self._add_info_in_file(list_with_info)
        return list_with_url

    def get_id_by_screen_name(self, screen_name: str) -> id:
        url = 'https://api.vk.com/method/utils.resolveScreenName'
        params = {
            'screen_name': screen_name
        }
        response = requests.get(url, params={**self.params, **params}).json()
        self._check_error(response)
        if len(response['response']) != 0:
            return str(response['response']['object_id'])

    def get_album_info(self, user_id):
        url = 'https://api.vk.com/method/photos.getAlbums'
        params = {
            'owner_id': user_id,
            'need_system': 1
        }
        response = requests.get(url, params={**self.params, **params}).json()
        self._check_error(response)
        albums = {
            str(number + 1) + ': ' + item['title']: [str(item['id']), item['size']] for
            number, item in enumerate(response['response']['items'])
        }
        return albums

    @staticmethod
    def exception_block(error):
        if 'list index out of range' in str(error):
            print(f'Album not found.\n')
        elif 'not integer' in str(error) or 'screen_name is undefined' in str(error):
            print(f'User not found.\n')
        elif 'invalid literal for int' in str(error):
            print(f'Amount of photos or album number is incorrect.\n')
        else:
            print(f'{error}.\n')

    @staticmethod
    def _check_error(response):
        if list(response.keys())[0] == 'error':
            raise Exception(f"{response['error']['error_msg']}")

    @staticmethod
    def _create_new_json_file():
        with open('info.json', 'w', encoding='UTF-8') as file:
            pass

    @staticmethod
    def _get_info_from_response(response, list_with_info, list_with_url):
        for item in response['response']['items']:
            if len(list_with_info) == 0:
                list_with_info.append({
                    "file_name": f"{str(item['likes']['count'])}.jpg",
                    "size": item['sizes'][-1]['type']
                })
                list_with_url.append({
                    "file_name": f"{str(item['likes']['count'])}.jpg",
                    "url": item['sizes'][-1]['url']
                })
            else:
                flag = False
                for dict in list_with_info:
                    if f"{str(item['likes']['count'])}.jpg" in dict["file_name"]:
                        flag = True
                if flag is False:
                    list_with_info.append({
                        "file_name": f"{str(item['likes']['count'])}.jpg",
                        "size": item['sizes'][-1]['type']
                    })
                    list_with_url.append({
                        "file_name": f"{str(item['likes']['count'])}.jpg",
                        "url": item['sizes'][-1]['url']
                    })
                else:
                    time = datetime.utcfromtimestamp(item['date']).strftime('%Y-%m-%d %H:%M:%S')
                    list_with_info.append({
                        "file_name": f"{str(time)}_{str(item['likes']['count'])}.jpg",
                        "size": item['sizes'][-1]['type']
                    })
                    list_with_url.append({
                        "file_name": f"{str(time)}_{str(item['likes']['count'])}.jpg",
                        "url": item['sizes'][-1]['url']
                    })

    @staticmethod
    def _add_info_in_file(list_with_info):
        with open('info.json', 'r+', encoding='UTF-8') as file:
                json.dump(list_with_info, file, indent="")
