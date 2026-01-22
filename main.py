import sys
import requests
import json
from time import sleep
from tqdm import tqdm

# Класс для работы с API ЯндексДиска
class YandexDiskAPI:
    main_url = 'https://cloud-api.yandex.net/v1/disk/resources'

    def __init__(self, token):
        self.headers = {'Authorization': f'OAuth {token}'}

    # Функция создаёт папку на ЯндексДиске
    def create_folder(self, folder):
        params = {'path': folder}
        response = requests.put(self.main_url,
                                headers = self.headers,
                                params = params)
        return response.status_code

    # Функция удаляет папку с ЯндексДиска
    def delete_folder(self, folder):
        params = {'path': folder}
        response = requests.put(self.main_url,
                                headers = self.headers,
                                params = params)
        return response.status_code == 204

    # Функция записывает файл на ЯндексДиск по пути path, полученный по ссылке url
    def upload_file(self, path, url):

        params = {'path': path, 'url': url}
        response = requests.post(f'{self.main_url}/upload', headers = self.headers,
                                 params = params)

        return response.status_code# == 202

    # Функция возвращает словарь из имени файла и его размера
    def file_size(self, filename):
        params = {'path': filename}
        response = requests.get(self.main_url, headers = self.headers,
                                params = params)
        result = {'filename': filename, 'size': response.json()['size']}
        return result

    # Функция записывает json-файл с компьютера на ЯндексДиск
    def save_json_yd(self, path_d, path_yd):
        params = {'path': path_yd}
        response_upload = requests.get(f'{self.main_url}/upload',
                                       headers=self.headers, params=params)
        upload_link = response_upload.json()['href']

        with open(path_d, 'r') as f:
            requests.put(upload_link, files={'file': f})
        pass

#Класс для работы с API сайта картинок собак

class DogAPI:
    main_url = 'https://dog.ceo/api/breed'

    def __init__(self, breed):
        self.breed = breed


    # Функция проверяет наличие породы в базе данных
    def is_breed_exist(self):
        response = requests.get(f'{self.main_url}/{self.breed}/images/random')
        return response.status_code == 200


    # Функция выводит список под-пород собаки
    def sub_breed_list(self):
        url = f'{self.main_url}/{self.breed}/list'
        response = requests.get(url)
        return response.json()['message']

    # Функция выдаёт ссылку случайной картинки породы собаки
    def image_url(self, sub_breed):
        results = []
        if not self.sub_breed_list():
            image_url = f'{self.main_url}/{self.breed}/images/random'
        else:
            image_url = f'{self.main_url}/{self.breed}/{sub_breed}/images/random'
        return requests.get(image_url).json()['message']

    # Функция выдаёт имя файла по ссылке случайной породы собаки
    def image_filename(self, url):
        return url.split('/')[-2] + '_' + url.split('/')[-1]


    # Функция выдаёт ссылку (список ссылок) с картинкой(ками) породы(всех под-пород)
    # собаки

    def image_url_list(self, sub_breed):
        if not self.sub_breed_list():
            image_url = f'{self.main_url}/{self.breed}/images/random'

        else:
            image_url = f'{self.main_url}/{self.breed}/{sub_breed}/images/random'

print('Программа для резервного копирования изображений пород собак с сайта https://dog.ceo.')
breed = input('Введите породу собаки на английском языке: ').strip().lower()
my_dog = DogAPI(breed)

if not my_dog.is_breed_exist():
    print('Такая порода не найдена')
    sys.exit(0)

yd_token = input('Введите токен ЯндексДиска:')
info_file = []
path_yd = input('Введите имя папки для копирования:')
my_dog_yd = YandexDiskAPI(yd_token)
my_dog_yd.create_folder(f'{path_yd}')
if my_dog_yd.create_folder(f'{path_yd}/{breed}') == 201:
    print(f'Папка {path_yd} успешно создана на ЯндексДиске')
elif my_dog_yd.create_folder(f'{path_yd}/{breed}') == 409:
    print(f'Папка {path_yd} уже существует на ЯндексДиске')
elif my_dog_yd.create_folder(f'{path_yd}/{breed}') == 401:
    print(f'Не правильный токен для авторизации на ЯндексДиске')
    sys.exit(0)

if len(my_dog.sub_breed_list()) == 0: # если у породы нет под-пород
    for i in tqdm(range(1)):
        image_url = my_dog.image_url(breed)
        image_filename = my_dog.image_filename(image_url)
        my_dog_yd.upload_file(f'{path_yd}/{breed}/{image_filename}', image_url)
        sleep(3)
        info_file.append(my_dog_yd.file_size(f'{path_yd}/{breed}/{image_filename}'))
else:

    for sub_breed in tqdm(my_dog.sub_breed_list()):
        image_url = my_dog.image_url(sub_breed)
        image_filename = my_dog.image_filename(image_url)
        my_dog_yd.upload_file(f'{path_yd}/{breed}/{image_filename}', image_url)
        sleep(3)
        info_file.append(my_dog_yd.file_size(f'{path_yd}/{breed}/{image_filename}'))


with open("info.json", "w", encoding="utf-8") as file:
    json.dump(info_file, file, ensure_ascii=False)
my_dog_yd.save_json_yd('info.json', f'{path_yd}/{breed}/info.json')
print('Программа успешно закончила работу.')