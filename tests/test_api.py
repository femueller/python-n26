from n26 import api, config
from n26.api import GET
from tests.test_api_base import N26TestBase, mock_auth_token, mock_api


class ApiTests(N26TestBase):
    """Common Api tests"""

    @mock_auth_token
    def test_get_token(self):
        expected = '12345678-1234-1234-1234-123456789012'
        token = self._underTest.get_token()
        self.assertEqual(token, expected)

    def test_init_without_config(self):
        api_client = api.Api()
        self.assertIsNotNone(api_client, config)

    def test_init_with_config(self):
        conf = config.Config(username='john.doe@example.com',
                             password='$upersecret')
        api_client = api.Api(conf)
        self.assertIsNotNone(api_client, config)
        self.assertEqual(api_client.config, conf)

    @mock_api(GET, "account_info.json")
    def test_get_account_info(self):
        info = self._underTest.get_account_info()
        self.assertEqual(info["email"], "john.doe@example.com")
