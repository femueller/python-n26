import os
import sys
from collections import namedtuple

import yaml

Config = namedtuple('Config', ['username', 'password'])


def get_config():
    # try to get values from ENV
    username, password = [os.environ.get(e)
                          for e in ["N26_USER", "N26_PASSWORD"]]

    if not username or not password:
        # print('Environment variables not set. trying to load cfg')

        config_file = os.path.expanduser('~/.config/n26.yml')
        if not os.path.exists(config_file):
            print('Neither environment variables nor config file could be found.')
            sys.exit(1)
        with open(config_file, 'r') as ymlfile:
            cfg = yaml.load(ymlfile)

            username = cfg['n26']['username']
            password = cfg['n26']['password']

    return Config(username, password)
