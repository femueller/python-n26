from n26 import api, config
from n26.api import BASE_URL_DE, POST, GET
from tests.test_api_base import N26TestBase, mock_auth_token, mock_requests


class ApiTests(N26TestBase):
    """Common Api tests"""

    def test_create_request_url(self):
        from n26.util import create_request_url
        expected = "https://api.tech26.de?bar=baz&foo=bar"
        result = create_request_url(BASE_URL_DE, {
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
        api_client = api.Api(self.config)
        result = api_client.get_token()
        self.assertEqual(result, expected)

    @mock_requests(url_regex=".*/token", method=POST, response_file="refresh_token.json")
    def test_refresh_token(self):
        refresh_token = "12345678-1234-abcd-abcd-1234567890ab"
        expected = "12345678-1234-abcd-abcd-1234567890ab"
        result = self._underTest._refresh_token(refresh_token)
        self.assertEqual(result['access_token'], expected)

    def test_init_without_config(self):
        api_client = api.Api()
        self.assertIsNotNone(api_client.config)

    def test_init_with_config(self):
        from container_app_conf.source.yaml_source import YamlSource
        conf = config.Config(singleton=False, data_sources=[
            YamlSource("test_creds", "./tests/")
        ])
        api_client = api.Api(conf)
        self.assertIsNotNone(api_client.config)
        self.assertEqual(api_client.config, conf)
