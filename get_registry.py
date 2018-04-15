import os
import shutil
from multiprocessing import Pool
from urllib.error import URLError, HTTPError
from urllib.request import urlretrieve


LOCAL_DIR = 'phone_registry'
BASE_URL = 'https://www.rossvyaz.ru/docs/articles/'
FILENAMES = ['DEF-9x', 'ABC-8x', 'ABC-3x', 'ABC-4x']


def get_registry_file(filename):
    print(f'Downloading {filename} ...')
    local_file = f'{LOCAL_DIR}/{filename}_source.csv'
    try:
        urlretrieve(f'{BASE_URL}{filename}.csv', local_file)
    except (URLError, HTTPError) as err:
        print(f'Error: {err}')
    else:
        print(f'{filename} downloaded')
    fix_encoding(local_file, filename)


def fix_encoding(local_file, filename):
    out_file = f'{LOCAL_DIR}/{filename}.csv'
    source = open(local_file, 'r', encoding='windows-1251')
    output = open(out_file, 'w', encoding='utf-8')
    with source, output:
        while True:
            chunk = source.read(4096)
            if not chunk:
                break
            output.write(chunk)
    os.remove(local_file)
    print(f'{filename} encoding fixed')


def download_files():
    if os.path.exists(LOCAL_DIR):
        shutil.rmtree(LOCAL_DIR)
    os.mkdir(LOCAL_DIR)
    with Pool() as pool:
        pool.map(get_registry_file, FILENAMES)


if __name__ == '__main__':
    download_files()
