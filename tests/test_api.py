import functools
import mock
from n26 import api, config
import pytest

conf =  config.Config(username='john.doe@example.com',
                                                password='$upersecret', card_id="123456789")

# decorator for patching get_token
def patch_token(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        with mock.patch('n26.api.Api.get_token') as mock_token:
            mock_token.return_value = 'some token'
            return func(*args, **kwargs)
    return wrapper


@pytest.fixture
def api_object():
    new_api = api.Api(conf)
    return new_api


# test __init__
@mock.patch('n26.api.config.get_config')
def test_init_implicit(patched_config):
    patched_config.return_value = conf
    new_api = api.Api()
    assert new_api.config == conf


def test_init_explicit():
    new_api = api.Api(conf)
    assert new_api.config == conf


# test token
def test_get_token():
    with mock.patch('n26.api.requests.post') as mock_post:
       mock_post.return_value.json.return_value = {
           'access_token': '12345678-1234-1234-1234-123456789012',
           'token_type': 'bearer',
           'refresh_token': '12345678-1234-1234-1234-123456789012',
           'expires_in': 1798,
           'scope': 'trust',
           'host_url': 'https://api.tech26.de'
       }
       new_api = api.Api(conf)
       token = new_api._get_token()
    assert token  == 'some token'


# test rest
@patch_token
def test_get_account_info(api_object):
    with mock.patch('n26.api.requests.get') as mock_get:
        mock_get.return_value.json.return_value = {'email':
                'john.doe@example.com'}
        info = api_object.get_account_info()
    assert info  == {'email': 'john.doe@example.com'}
