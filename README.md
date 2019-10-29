# N26 Python CLI/API
[![Build Status](https://travis-ci.org/femueller/python-n26.svg?branch=master)](https://travis-ci.org/femueller/python-n26)
[![PyPI version](https://img.shields.io/github/pipenv/locked/python-version/femueller/python-n26)](https://img.shields.io/github/pipenv/locked/python-version/femueller/python-n26)
[![PyPI version](https://badge.fury.io/py/n26.svg)](https://badge.fury.io/py/n26)
[![Downloads](https://img.shields.io/pypi/dm/n26.svg)](https://img.shields.io/pypi/dm/n26.svg)

- [N26 Python CLI/API](#N26-Python-CLIAPI)
  - [About](#About)
  - [Install](#Install)
  - [Configuration](#Configuration)
  - [Usage](#Usage)
    - [CLI example](#CLI-example)
    - [API example](#API-example)
  - [Projects using python-n26](#Projects-using-python-n26)
  - [Contribute](#Contribute)
    - [Run locally](#Run-locally)
  - [Maintainers](#Maintainers)
  - [Credits](#Credits)
  - [Disclaimer](#Disclaimer)
  
[![asciicast](https://asciinema.org/a/260083.svg)](https://asciinema.org/a/260083)

## About
[python-n26](https://github.com/femueller/python-n26) is a Python 3.6+ library and Command Line Interface to request information from n26 bank accounts. You can use it to check your balance from the terminal or include it in your own Python projects.

**Disclaimer:** This is an unofficial community project which is not affiliated with N26 GmbH/N26 Inc.

## Install

```shell
pip3 install n26
wget https://raw.githubusercontent.com/femueller/python-n26/master/n26.yml.example -O ~/.config/n26.yml
# configure username and password
vim ~/.config/n26.yml
```

## Configuration

python-n26 uses [container-app-conf](https://github.com/markusressel/container-app-conf) to provide different options for configuration.
You can place a YAML (`n26.yaml` or `n26.yml`) or TOML (`n26.toml` or `n26.tml`) configuration file in `./`, `~/` or `~/.config/`. Have a look at the [YAML example](n26.yml.example) and [TOML example](n26.tml.example).
If you want to use environment variables:

- `N26_USER`: username
- `N26_PASSWORD`: password
- `N26_LOGIN_DATA_STORE_PATH`: optional **file** path to store login data (recommended for cli usage)
- `N26_MFA_TYPE`: `app` will use the paired app as 2 factor authentication, `sms` will use SMS to the registered number.

Note that **when specifying both** environment variables as well as a config file and a key is present in both locations the **enviroment variable values will be preferred**.

## Authentication

Since 14th of September 2019 N26 requires a login confirmation (2 factor authentication). 

There are two options here:

1. Using the paired phone N26 app to approve login on devices that are not paired. This can be configured by setting `app` as the `mfa_type`. You will receive a notification on your phone when you start using this library to request data. python-n26 checks for your login confirmation every 5 seconds. If you fail to approve the login request within 60 seconds an exception is raised.
2. Using a code delivered via SMS to your registered phone number as 2 factor authentication. This can be configured by setting `sms` as the `mfa_type`.

If you do not specify a `login_data_store_path` this login information is only stored in memory. In order to avoid that every CLI command requires a new confirmation, the login data retrieved in the above process can be stored on the file system. Please note that **this information must be protected** from the eyes of third parties **at all costs**. You can specify the location to store this data in the [Configuration](#Configuration).

## Usage

### CLI example

```shell
> n26 balance
123.45 EUR
```

Or if using environment variables:

```bash
> N26_USER=user N26_PASSWORD=passwd N26_MFA_TYPE=app n26 balance
123.45 EUR
```

### JSON output
If you would like to work with the raw `JSON` rather than the pretty table 
layout you can use the global `-json` parameter:

```bash 
> n26 -json balance
{
  "id": "12345678-1234-1234-1234-123456789012",
  "physicalBalance": null,
  "availableBalance": 123.45,
  "usableBalance": 123.45,
  "bankBalance": 123.45,
  "iban": "DE12345678901234567890",
  "bic": "NTSBDEB1XXX",
  "bankName": "N26 Bank",
  "seized": false,
  "currency": "EUR",
  "legalEntity": "EU",
  "users": [
    {
      "userId": "12345678-1234-1234-1234-123456789012",
      "userRole": "OWNER"
    }
  ],
  "externalId": {
    "iban": "DE12345678901234567890"
  }
}
```


### API example
```python
from n26 import api
balance = api.Api()
print(balance.get_balance())
```

This is going to use the same mechanism to load configuration as the CLI tool, to specify your own configuration you can use it as:

```python
from n26.api import Api
from n26.config import Config

conf = Config(write_reference=False, validate=False)
conf.USERNAME.value = "john.doe@example.com"
conf.PASSWORD.value = "$upersecret"
conf.LOGIN_DATA_STORE_PATH.value = None
conf.MFA_TYPE.value = "app"
conf.validate()

client = Api(conf)
print(client.get_balance())
```

## Projects using python-n26

The following projects are using [python-n26](https://github.com/femueller/python-n26):

* [home-assistant](https://github.com/home-assistant/home-assistant/tree/dev/homeassistant/components/n26): https://www.home-assistant.io/components/n26

## Contribute
If there are any issues, bugs or missing API endpoints, feel free to contribute by forking the project and creating a Pull-Request.

### Run locally

Prerequirements: [Pipenv](https://pipenv.readthedocs.io/)

```shell
git clone git@github.com:femueller/python-n26.git
cd python-n26
pipenv shell
pipenv install
python3 -m n26 balance
```

## Maintainers
* [Markus Ressel](https://github.com/markusressel)
* [Felix Mueller](https://github.com/femueller)

## Credits
* [Nick Jüttner](https://github.com/njuettner) for providing [the API authentication flow](https://github.com/njuettner/alexa/blob/master/n26/app.py)
* [Pierrick Paul](https://github.com/PierrickP/) for providing [the API endpoints](https://github.com/PierrickP/n26/blob/develop/lib/api.js)

## Disclaimer
This project is not affiliated with N26 GmbH/N26 Inc. if you want to learn more about it, visit https://n26.com/.
