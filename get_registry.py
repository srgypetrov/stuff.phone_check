import os
import shutil
from contextlib import closing
from multiprocessing import Pool
from urllib.error import URLError, HTTPError
from urllib.request import urlopen


LOCAL_DIR = 'phone_registry'
BASE_URL = 'https://www.rossvyaz.ru/docs/articles/'
FILENAMES = ['DEF-9x', 'ABC-8x', 'ABC-3x', 'ABC-4x']


def get_registry_file(filename):
    print(f'Downloading {filename} ...')
    try:
        response = urlopen(f'{BASE_URL}{filename}.csv')
    except (URLError, HTTPError) as err:
        print(f'Error: {err}')
        return
    filepath = f'{LOCAL_DIR}/{filename}.csv'
    with closing(response), open(filepath, 'w', encoding='utf-8') as file:
        while True:
            chunk = response.read(4096).decode('windows-1251')
            if not chunk:
                break
            file.write(chunk)
    print(f'{filename} downloaded')


def download_files():
    if os.path.exists(LOCAL_DIR):
        shutil.rmtree(LOCAL_DIR)
    os.mkdir(LOCAL_DIR)
    with Pool() as pool:
        pool.map(get_registry_file, FILENAMES)


if __name__ == '__main__':
    download_files()
