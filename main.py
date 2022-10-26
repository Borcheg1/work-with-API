import requests
import json
import tqdm
import time


class Vk:
    def __init__(self, auth_token: str):
        self.auth_token = auth_token
        self.params = {
            'access_token': auth_token,
            'v': '5.131'
        }

    def get_photos_url(self, user_id, album, count=5) -> list:
        url = 'https://api.vk.com/method/photos.get'
        params = {
            'owner_id': user_id,
            'album_id': album,
            'rev': 0,
            'extended': 1,
            'photo_size': 1,
            'count': count
        }
        response = requests.get(url, params={**self.params, **params}).json()
        self._check_error(response)
        self._add_info_in_json(response)
        list_with_info = self._get_info_from_json(response)
        return list_with_info

    def get_album_info(self, user_id):
        url = 'https://api.vk.com/method/photos.getAlbums'
        params = {
            'owner_id': user_id
        }
        response = requests.get(url, params={**self.params, **params}).json()
        self._check_error(response)
        albums = {
            str(number + 1) + ': ' + item['title']: str(item['id']) for number, item in
            enumerate(response['response']['items'])
        }
        albums['0: Профиль'] = 'profile'
        return albums

    @staticmethod
    def _check_error(response):
        if list(response.keys())[0] == 'error':
            raise Exception(f"{response['error']['error_msg']}")

    @staticmethod
    def _add_info_in_json(response):
        list_with_info = [{
            "file_name": f"{str(item['date'])}_{str(item['likes']['count'])}.jpg",
            "size": item['sizes'][-1]['type']}
            for item in response['response']['items']
        ]

        with open('info.json', 'w', encoding='UTF-8') as file:
            json.dump(list_with_info, file)

    @staticmethod
    def _get_info_from_json(response):
        info_from_json = [{
            "file_name": f"{str(item['date'])}_{str(item['likes']['count'])}.jpg",
            "url": item['sizes'][-1]['url']}
            for item in response['response']['items']
        ]
        return info_from_json


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


def main():
    ya_token = input(f'Введите OAuth-token Яндекс.Диска:\n')
    vk_token = ''
    test_ya = Ya(ya_token)
    test_vk = Vk(vk_token)
    user_id = input('Для выхода из программы введите "0"\n'
                    'Введите ID пользователя vk:\n')

    while user_id != '0':
        try:
            album_info = test_vk.get_album_info(user_id)
            album = sorted(album_info.keys(), key=lambda x: int(x.split(':')[0]))
            album_number = int(input(f'Введите номер альбома, '
                                     f'из которого хотите скачать фотографии:\n{album}\n'))
            list_with_info = test_vk.get_photos_url(user_id, album_info[album[album_number]])
        except Exception as error:
            if 'list index out of range' in str(error):
                print(f'album not found.\nПопробуйте снова. Для выхода из программы введите "0"')
                user_id = input('Введите ID пользователя vk:\n')
            else:
                print(f'{error}.\nПопробуйте снова. Для выхода из программы введите "0"')
                user_id = input('Введите ID пользователя vk:\n')
        else:
            if len(list_with_info) == 0:
                print(f'У пользователя нет фотографий.\n'
                      f'Попробуйте снова. Для выхода из программы введите "0"')
                user_id = input('Введите ID пользователя vk:\n')
            else:
                print('Фотографии получены, начинаю загрузку на Яндекс.Диск')
                break
    else:
        return

    folder_name = test_ya.create_folder(user_id, album[album_number])
    time.sleep(0.3)

    for index in tqdm.trange(len(list_with_info)):
        item = list_with_info[index]
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
