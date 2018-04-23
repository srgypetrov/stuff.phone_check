import os

import bottle

app = bottle.default_app()
base_path = os.path.abspath(os.path.dirname(__file__))
log_path = os.path.join(base_path, 'check.log')
bottle.TEMPLATE_PATH.insert(0, os.path.join(base_path, 'views'))


@bottle.route('/')
def index():
    return bottle.template('index')


@bottle.route('/result')
@bottle.route('/result/')
def result():
    if not os.path.exists(log_path):
        bottle.redirect('/')
    return bottle.template('result')


@bottle.route('/result_progress')
@bottle.route('/result_progress/')
def result_progress():
    with open(log_path) as logfile:
        log = logfile.read()
    data = process_log(log)
    return bottle.template('result_progress', **data)


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
    log_data = parse_log(log)
    return log_data


if __name__ == "__main__":
    bottle.run(host='localhost', port=8000, debug=True)
