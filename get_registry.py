import os
import shutil
from contextlib import closing
from multiprocessing import Pool
from urllib.error import URLError, HTTPError
from urllib.request import urlopen


DIR = 'phone_registry'
URL = 'https://www.rossvyaz.ru/docs/articles/'
FILENAMES = ['DEF-9x.csv', 'ABC-8x.csv', 'ABC-3x.csv', 'ABC-4x.csv']


def get_registry_file(filename):
    print(f'Downloading {filename} ...')
    try:
        response = urlopen(f'{URL}{filename}')
    except (URLError, HTTPError) as err:
        print(f'Error: {err}')
        return
    with closing(response), open(f'{DIR}/{filename}', 'w', encoding='utf-8') as file:
        while True:
            chunk = response.read(4096).decode('windows-1251')
            if not chunk:
                break
            file.write(chunk)
    print(f'{filename} downloaded')


def download_files():
    if os.path.exists(DIR):
        shutil.rmtree(DIR)
    os.mkdir(DIR)
    with Pool() as pool:
        pool.map(get_registry_file, FILENAMES)


if __name__ == '__main__':
    download_files()
