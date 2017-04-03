# N26 Python CLI/API
[![PyPI version](https://badge.fury.io/py/n26.svg)](https://badge.fury.io/py/n26)

The idea is to have a convenient command line interface for [n26](https://n26.com/) to:
* Request account balance
* Show transactions
* Enable to only use API component (subclass) to integrate into own application

## CLI
### CLI setup
    pip3 install n26
    wget https://raw.githubusercontent.com/femueller/python-n26/master/n26.yml.example -O ~/.config/n26.yml
    # configure username, password and card ID
    vim ~/.config/n26.yml

You can also specify environment variables with the credentials instead of creating a config file.

- N26_USER: username
- N26_PASSWORD: password
- N26_CARD_ID: card id

### CLI example
    n26 balance

Or if using environment variables:

    N26_USER=user N26_PASSWORD=passwd N26_CARD_ID:123456789 n26 balance

## API
### API setup
    pip3 install n26
    wget https://raw.githubusercontent.com/femueller/python-n26/master/n26.yml.example -O ~/.config/n26.yml
    # configure username and password
    vim ~/.config/n26.yml

### Using the API
    from n26 import api
    balance = api.Api()
    print(balance.get_balance())

This is going to use the same mechanism to load configuration as the CLI tool, to specify your own configuration you can use it as:

    from n26 import api
    from n26 import config
    conf = config.Config('username', 'passwd', 'card_id')
    balance = api.Api(conf)
    print(balance.get_balance())

## Run locally
    git clone git@github.com:femueller/python-n26.git
    cd python-n26
    python3 -m n26 balance

## Credits
* [Nick Jüttner](https://github.com/njuettner) for providing [the API authentication flow](https://github.com/njuettner/alexa/blob/master/n26/app.py)
* [Pierrick Paul](https://github.com/PierrickP/) for providing [the API endpoints](https://github.com/PierrickP/n26/blob/develop/lib/api.js)
