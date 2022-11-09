import configparser
import time

import tqdm

from VkClass import Vk
from YaClass import Ya
from GoogleDriveClass import Google


def main():
    ini_path = input('Введите путь до ini файла, где записаны токены\n'
                     '(в формате: C:\\Users\\Desktop\\tokens.ini):\n')
    tokens = configparser.ConfigParser()
    tokens.read(ini_path)

    ya_token = tokens['Ya']['token']
    vk_token = tokens['Vk']['token']
    vk_test = Vk(vk_token)
    ya_test = Ya(ya_token)
    google_test = Google()

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
            if album_number < 1:
                raise Exception('Album not found')
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
                print('Фотографии получены, куда хотите их загрузить?\n')
                download = input('Введите "1" для загрузки на Yandex.Disk\n'
                                 'Введите "2" для загрузки на Google.Drive\n'
                                 'Введите "3" для загрузки на Yandex.Disk и Google.Drive\n'
                                 'Введите любой другой символ для выхода из программы\n')
                break
    else:
        return

    folder_name = f'user {user_id}(album{album[album_number - 1].split(":")[1]})'

    if download in ['1', '3']:
        ya_test.create_folder(user_id, folder_name)
        time.sleep(0.5)

        for index in tqdm.trange(len(list_with_url)):
            item = list_with_url[index]
            file_name, url = list(item.values())
            response = ya_test.upload_file(url, file_name, folder_name)
            if 200 < response.status_code > 202:
                raise Exception(f'{response.json()["error"]}')
            time.sleep(0.5)
        print(
            f'\nФотографии успешно загружены '
            f'в папку "{folder_name}" на Яндекс.Диск'
        )

    if download in ['2', '3']:
        folder_id = google_test.create_folder(folder_name)
        time.sleep(0.5)

        for index in tqdm.trange(len(list_with_url)):
            item = list_with_url[index]
            file_name, url = list(item.values())
            response = google_test.upload_file(folder_id, url, file_name)
            if 200 < response.status_code > 202:
                raise Exception(f'Oops! Something went wrong')
            time.sleep(0.5)
        print(
            f'\nФотографии успешно загружены '
            f'в папку "{folder_name}" на Гугл.Диск'
        )


if __name__ == '__main__':
    main()
