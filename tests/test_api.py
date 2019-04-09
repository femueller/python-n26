from n26 import api, config
from n26.api import BASE_URL, POST, GET
from tests.test_api_base import N26TestBase, mock_auth_token, mock_requests, mock_config


class ApiTests(N26TestBase):
    """Common Api tests"""

    def test_create_request_url(self):
        expected = "https://api.tech26.de?bar=baz&foo=bar"
        result = self._underTest._create_request_url(BASE_URL, {
            "foo": "bar",
            "bar": "baz"
        })
        self.assertEqual(result, expected)

    @mock_requests(method=GET, response_file="refresh_token.json")
    def test_do_request(self):
        result = self._underTest._do_request(GET, "/something")
        self.assertIsNotNone(result)

    @mock_auth_token
    def test_get_token(self):
        expected = '12345678-1234-1234-1234-123456789012'
        result = self._underTest.get_token()
        self.assertEqual(result, expected)

    @mock_requests(url_regex=".*/token", method=POST, response_file="refresh_token.json")
    def test_refresh_token(self):
        expected = "12345678-1234-abcd-abcd-1234567890ab"
        result = self._underTest.get_token()
        self.assertIsNot(result, expected)
        result = self._underTest._refresh_token("bla")
        self.assertEqual(result["access_token"], expected)

    @mock_config()
    def test_init_without_config(self):
        api_client = api.Api()
        self.assertIsNotNone(api_client.config)

    def test_init_with_config(self):
        conf = config.Config(username='john.doe@example.com',
                             password='$upersecret')
        api_client = api.Api(conf)
        self.assertIsNotNone(api_client.config)
        self.assertEqual(api_client.config, conf)
