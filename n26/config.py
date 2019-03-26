import yaml
import os
from collections import namedtuple

Config = namedtuple('Config', ['username', 'password', 'card_id'])


def get_config():
    # try to get values from ENV
    username, password, card_id = [os.environ.get(e)
                                   for e in ["N26_USER", "N26_PASSWORD", "N26_CARD_ID"]]

    if not username or not password or not card_id:
        # print('Environment variables not set. trying to load cfg')

        config_file = os.path.expanduser('~/.config/n26.yml')
        with open(config_file, 'r') as ymlfile:
            cfg = yaml.load(ymlfile)

            username = cfg['n26']['username']
            password = cfg['n26']['password']
            card_id = cfg['n26']['card_id']

    return Config(username, password, card_id)
