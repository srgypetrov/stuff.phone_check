import json
import os
import subprocess

import bottle


DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(DIR)
LOG_PATH = os.path.join(DIR, 'check.log')
PID_PATH = os.path.join(BASE_DIR, 'check.pid')
META_PATH = os.path.join(BASE_DIR, 'registry/meta.json')
CHECK_PATH = os.path.join(BASE_DIR, 'rust/target/release/check_hash')

app = bottle.default_app()
bottle.TEMPLATE_PATH.insert(0, DIR)


@bottle.route('/')
def index():
    return bottle.template('app')


@bottle.route('/start', method='POST')
@bottle.route('/start/', method='POST')
def start():
    if os.path.isfile(PID_PATH):
        return {
            'success': False,
            'message': 'Process already running'
        }
    hashes_data = bottle.request.json.get('hashes', '')
    valid, data = validate_hashes(hashes_data)
    if not valid:
        return {
            'success': False,
            'message': data
        }
    with open(LOG_PATH, 'w') as logfile:
        subprocess.Popen([CHECK_PATH, *data], stdout=logfile)
    return {
        'success': True
    }


@bottle.route('/result')
@bottle.route('/result/')
def result():
    if not os.path.isfile(LOG_PATH):
        return {}
    with open(LOG_PATH) as logfile:
        log = logfile.read()
    return process_log(log)


def get_progress(line_info):
    fileno, filename, lineno = line_info.split()
    with open(META_PATH) as metafile:
        meta = json.load(metafile)
    lines_count = meta.get(filename, 0)
    percent = float(lineno) / float(lines_count) * 100
    return {
        'percent': round(percent),
        'fileno': int(fileno),
    }


def parse_log(log):
    data = {}
    for line in log.splitlines()[::-1]:
        key, value = line.split(':')
        key = key.lower()
        if key in ('phone', 'unknown'):
            data.setdefault(key, []).append(value)
        elif key in data:
            continue
        else:
            data[key] = value
    return data


def process_log(log):
    data = {}
    log_data = parse_log(log)
    line = log_data.get('line')
    runtime = log_data.get('runtime')
    phones = log_data.get('phone')
    unknown = log_data.get('unknown')
    error = log_data.get('error')
    if line is not None:
        data.update(get_progress(line))
    if runtime is not None:
        spent = int(runtime)
        data.update({'spent': f'{spent // 60}:{spent % 60}'})
    if phones is not None:
        data.update({'phones': [p.split() for p in phones]})
    if unknown is not None:
        data.update({'unknown': unknown})
    if error is not None:
        data.update({'error': error})
    return data


def validate_hashes(hashes_data):
    valid_hashes = []
    if not hashes_data.strip():
        return False, 'No hashes specified'
    for item in hashes_data.split(','):
        item = item.strip()
        if len(item) != 40:
            return False, f'Value is not 40-digit number: {item}'
        try:
            int(item, 16)
        except ValueError:
            return False, f'Value is not hexidecimal number: {item}'
        valid_hashes.append(item)
    return True, valid_hashes


if __name__ == "__main__":
    bottle.run(host='127.0.0.1', port=8000, debug=True)
