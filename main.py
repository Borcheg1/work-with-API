import requests
import json
import tqdm
import time
from datetime import datetime
from Vk_class import Vk
from Ya_class import Ya


def main():
    ya_token = input(f'Введите OAuth-token Яндекс.Диска:\n')
    vk_token = ''
    vk_test = Vk(vk_token)
    ya_test = Ya(ya_token)

    user_id = input('Для выхода из программы введите "0"\n'
                    'Введите ID или nickname пользователя vk:\n')

    while user_id != '0':
        try:
            screen_name = vk_test.get_id_by_screen_name(user_id)

            if screen_name is not None:
                user_id = screen_name

            album_info = vk_test.get_album_info(user_id)
            album = sorted(album_info.keys(), key=lambda x: int(x.split(':')[0]))
            album_number = int(input(f'Введите номер альбома, '
                                     f'из которого хотите скачать фотографии:\n{album}\n'))
            list_with_url = vk_test.get_photos_url(user_id, album_info[album[album_number - 1]])

        except Exception as error:
            vk_test.exception_block(error)
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

    folder_name = ya_test.create_folder(user_id, album[album_number - 1])
    time.sleep(0.3)

    for index in tqdm.trange(len(list_with_url)):
        item = list_with_url[index]
        file_name, url = list(item.values())
        response = ya_test.upload_file(url, file_name, folder_name)
        if 200 < response.status_code > 202:
            raise Exception(f'{response.json()["error"]}')
        time.sleep(0.3)
    print(
        f'\nФотографии успешно загружены '
        f'в папку "{folder_name}" на Яндекс.Диск'
    )


if __name__ == '__main__':
    main()
