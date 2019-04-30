# N26 Python CLI/API
[![Build Status](https://travis-ci.org/femueller/python-n26.svg?branch=master)](https://travis-ci.org/femueller/python-n26)
[![PyPI version](https://badge.fury.io/py/n26.svg)](https://badge.fury.io/py/n26)
[![Downloads](https://img.shields.io/pypi/dm/n26.svg)](https://img.shields.io/pypi/dm/n26.svg)
[![Join Discord](https://img.shields.io/badge/Discord-Join-7289DA.svg)](https://discord.gg/u7fEzS)

- [N26 Python CLI/API](#n26-python-cliapi)
  - [About](#about)
  - [Install](#install)
  - [Usage](#usage)
    - [CLI example](#cli-example)
    - [API example](#api-example)
  - [Projects using python-n26](#projects-using-python-n26)
  - [Contribute](#contribute)
    - [Run locally](#run-locally)
  - [Credits](#credits)

## About
[python-n26](https://github.com/femueller/python-n26) is a Command Line Interface to request information from n26 bank accounts and a Python 3 module that can be used in Python projects.

**Disclaimer:** This is an unofficial community project which is not affiliated with N26 GmbH/N26 Inc.

## Install

    pip3 install n26
    wget https://raw.githubusercontent.com/femueller/python-n26/master/n26.yml.example -O ~/.config/n26.yml
    # configure username and password
    vim ~/.config/n26.yml

You can also specify environment variables with the credentials.

- N26_USER: username
- N26_PASSWORD: password

Note that **when specifying both** environment variables as well as a config file their values can be merged.
When there is a conflict however (i.e. a key is present in both locations) the **enviroment variable values will be preferred**.

## Usage

### CLI example
    n26 balance

Or if using environment variables:

    N26_USER=user N26_PASSWORD=passwd n26 balance

### API example
    from n26 import api
    balance = api.Api()
    print(balance.get_balance())

This is going to use the same mechanism to load configuration as the CLI tool, to specify your own configuration you can use it as:

    from n26 import api
    from n26 import config
    conf = config.Config('username', 'passwd')
    client = api.Api(conf)
    print(client.get_balance())

## Projects using python-n26

The following projects are using [python-n26](https://github.com/femueller/python-n26):

* [home-assistant](https://github.com/home-assistant/home-assistant/tree/dev/homeassistant/components/n26): https://www.home-assistant.io/components/n26

## Contribute
If there are any issues, bugs or missing API endpoints, feel free to contribute by forking the project and creating a Pull-Request.

### Run locally

Prerequirements: [Pipenv](https://pipenv.readthedocs.io/)

    git clone git@github.com:femueller/python-n26.git
    cd python-n26
    pipenv shell
    pipenv install
    python3 -m n26 balance

## Credits
* [Nick Jüttner](https://github.com/njuettner) for providing [the API authentication flow](https://github.com/njuettner/alexa/blob/master/n26/app.py)
* [Pierrick Paul](https://github.com/PierrickP/) for providing [the API endpoints](https://github.com/PierrickP/n26/blob/develop/lib/api.js)
