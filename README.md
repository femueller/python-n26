# N26 Python CLI/API
The idea is to have a convenient command line interface for [n26](https://n26.com/) to:
* Request account balance
* Make transactions
* Enable to only use API component (subclass) to integrate into own application

## CLI
### CLI setup
    pip3 install n26
    wget https://raw.githubusercontent.com/femueller/python-n26/master/n26.yml.example ~/.config/n26.yml
    # configure username, password and card ID
    vim ~/.config/n26.yml

### CLI example
    n26 balance

## API
### Api setup
    pip3 install n26
    wget https://raw.githubusercontent.com/femueller/python-n26/master/n26.yml.example -O ~/.config/n26.yml
    # configure username and password
    vim ~/.config/n26.yml

### Using the API
    from n26 import api
    balance = api.Api()
    print(balance.get_balance())

## Run locally
    git clone git@github.com:femueller/python-n26.git
    cd python-n26
    python3 -m n26 balance

## Credits
* [Nick Jüttner](https://github.com/njuettner) for providing [the API authentication flow](https://github.com/njuettner/alexa/blob/master/n26/app.py)
* [Pierrick Paul](https://github.com/PierrickP/) for providing [the API endpoints](https://github.com/PierrickP/n26/blob/develop/lib/api.js)
