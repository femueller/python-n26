import yaml
import os

config_file = os.path.expanduser('~/.config/n26.yml')

# Load config.yml
with open(config_file, 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

username = cfg['n26']['username']  # TODO: or os.environ['N26_USER']
password = cfg['n26']['password']  # TODO: or os.environ['N26_PASSWORD']
