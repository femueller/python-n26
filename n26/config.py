import yaml
import os

config_file = os.path.expanduser('~/.config/n26.yml')

# if os.environ['N26_USER'] and os.environ['N26_PASSWORD'] is None:
#    print('Environment variables not set. trying to load cfg')
# Load config.yml
with open(config_file, 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

    username = cfg['n26']['username']  # TODO: or os.environ['N26_USER']
    password = cfg['n26']['password']  # TODO: or os.environ['N26_PASSWORD']
    card_id = cfg['n26']['card_id']  # TODO: or os.environ['N26_PASSWORD']
# else:
#    username = os.environ['N26_USER']
#    password = os.environ['N26_PASSWORD']
