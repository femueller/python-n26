import mock
import pytest

from n26 import api, config
from tests.test_api_base import N26TestBase, mock_auth_token

conf = config.Config(username='john.doe@example.com',
                     password='$upersecret')


class ApiTests(N26TestBase):

    @mock_auth_token
    def test_get_token(self):
        expected = '12345678-1234-1234-1234-123456789012'
        new_api = api.Api(conf)
        token = new_api.get_token()
        self.assertEqual(token, expected)


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


# test rest
@mock_auth_token
def test_get_account_info(api_object):
    with mock.patch('n26.api.requests.get') as mock_get:
        mock_get.return_value.json.return_value = {'email': 'john.doe@example.com'}
        info = api_object.get_account_info()
    assert info == {'email': 'john.doe@example.com'}
