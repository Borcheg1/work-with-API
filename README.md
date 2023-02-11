# Программа для сохранения на Yandex или Google диск изображений с ресурса VK.
Программа позволяет найти альбомы с изображениями по ID или nickname человека на ресурсе VK, выбрать нужное количество изображений и загрузить их на Yandex или Google диск.  Так же программа записывает в json файл информацию о загруженных изображениях в виде:  

    "file_name": "количество лайков на данном изображении",
    "size": "тип размера изображения"

В случае, если количество лайков у изображений совпадает, информация будет записана в следующем виде:  

    "file_name": "дата загрузки изображения _ количество лайков",
    "size": "тип размера изображения"

