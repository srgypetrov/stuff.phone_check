import os
from contextlib import closing
from functools import partial
from multiprocessing import Pool

import requests


BASE_PATH = os.path.abspath(os.path.dirname(__file__))
FILES_URL = 'https://www.rossvyaz.ru/docs/articles/'
FINGERPRINT_URL = 'https://www.rossvyaz.ru/fp/awasah/'
FILE_NAMES = ['DEF-9x.csv', 'ABC-8x.csv', 'ABC-3x.csv', 'ABC-4x.csv']


def get_registry_file(cookies, filename):
    print(f'Downloading {filename} ...')
    with requests.Session() as session:
        response = session.get(
            f'{FILES_URL}/{filename}',
            cookies=cookies
        )
    filepath = os.path.join(BASE_PATH, filename)
    with closing(response), open(filepath, 'w', encoding='utf-8') as file:
        for chunk in response.iter_content(4096):
            file.write(chunk.decode('windows-1251'))
    print(f'{filename} downloaded')


def get_cookies():
    fingerprint = os.path.join(BASE_PATH, 'fingerprint.xml')
    with open(fingerprint) as file:
        xml = file.read()
    with requests.Session() as session:
        session.options(FINGERPRINT_URL)
        session.post(
            FINGERPRINT_URL,
            headers={"Content-type": "application/xml"},
            data=xml
        )
        return session.cookies.get_dict()


def download_files():
    cookies = get_cookies()
    download = partial(get_registry_file, cookies)
    with Pool() as pool:
        pool.map(download, FILE_NAMES)


if __name__ == '__main__':
    download_files()
