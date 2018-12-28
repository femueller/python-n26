import pytest
import mock
from n26 import config
import os
import sys

PATH = os.path.dirname(os.path.abspath(__file__))
test_creds = os.path.join(PATH, "test_creds.yml")

def test_preconditions():
    assert os.path.exists(test_creds)

@mock.patch.dict(os.environ, {"N26_USER": "john.doe@example.com", "N26_PASSWORD": "$upersecret", "N26_CARD_ID": "123456789"})
def test_environment_variable():
    assert config.get_config() == config.Config(username='john.doe@example.com',
                                                password='$upersecret', card_id="123456789")

# ensure environment is empty
@mock.patch.dict(os.environ, {"N26_USER": "", "N26_PASSWORD": "", "N26_CARD_ID": ""})
def test_file(monkeypatch):
    # patch path to local test file
    def mockreturn(path):
        return test_creds
    monkeypatch.setattr(os.path, "expanduser", mockreturn)
    assert config.get_config() == config.Config(username='john.doe@example.com',
                                                password='$upersecret', card_id="123456789")
