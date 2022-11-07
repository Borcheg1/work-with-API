import requests
import json
import tqdm
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

        self.create_new_json_file()

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
    def _check_error(response):
        if list(response.keys())[0] == 'error':
            raise Exception(f"{response['error']['error_msg']}")

    @staticmethod
    def create_new_json_file():
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

    def create_folder(self, user_id, album):
        main_url = 'https://cloud-api.yandex.net/v1/disk/resources'
        folder_name = f'user {user_id}(album{album.split(":")[1]})'
        params = {'path': folder_name}
        response = requests.put(main_url, headers=self.headers, params=params)
        if response.status_code != 201:
            raise Exception(f'{response.json()["error"]}')
        return folder_name


def exception_block(error):
    if 'list index out of range' in str(error):
        print(f'Album not found.\n')
    elif 'not integer' in str(error) or 'screen_name is undefined' in str(error):
        print(f'User not found.\n')
    elif 'invalid literal for int' in str(error):
        print(f'Amount of photos or album number is incorrect.\n')
    else:
        print(f'{error}.\n')


def main():
    ya_token = input(f'Введите OAuth-token Яндекс.Диска:\n')
    vk_token = ''
    test_ya = Ya(ya_token)
    test_vk = Vk(vk_token)
    user_id = input('Для выхода из программы введите "0"\n'
                    'Введите ID или nickname пользователя vk:\n')

    while user_id != '0':
        try:
            screen_name = test_vk.get_id_by_screen_name(user_id)

            if screen_name is not None:
                user_id = screen_name

            album_info = test_vk.get_album_info(user_id)
            album = sorted(album_info.keys(), key=lambda x: int(x.split(':')[0]))
            album_number = int(input(f'Введите номер альбома, '
                                     f'из которого хотите скачать фотографии:\n{album}\n'))
            list_with_url = test_vk.get_photos_url(user_id, album_info[album[album_number - 1]])

        except Exception as error:
            exception_block(error)
            print('Попробуйте снова. Для выхода из программы введите "0"')
            user_id = input('Введите ID или nickname пользователя vk:\n')
        else:
            if len(list_with_url) == 0:
                print(f'Photos not found.\n'
                      f'Попробуйте снова. Для выхода из программы введите "0"')
                user_id = input('Введите ID или nickname пользователя vk:\n')
            else:
                print('Фотографии получены, начинаю загрузку на Яндекс.Диск')
                break
    else:
        return

    folder_name = test_ya.create_folder(user_id, album[album_number - 1])
    time.sleep(0.3)

    for index in tqdm.trange(len(list_with_url)):
        item = list_with_url[index]
        file_name, url = list(item.values())
        response = test_ya.upload_file(url, file_name, folder_name)
        if 200 < response.status_code > 202:
            raise Exception(f'{response.json()["error"]}')
        time.sleep(0.3)
    print(
        f'\nФотографии успешно загружены '
        f'в папку "{folder_name}" на Яндекс.Диск'
    )


if __name__ == '__main__':
    main()
