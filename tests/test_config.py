import os

import mock

from n26 import config
from n26.config import ENV_PARAM_USER, ENV_PARAM_PASSWORD
from tests.test_api_base import N26TestBase


class ConfigTests(N26TestBase):
    PATH = os.path.dirname(os.path.abspath(__file__))
    CONFIG_FILE = os.path.join(PATH, "test_creds.yml")

    EXPECTED_FILE_CONF = config.Config(username='john.doe@file.com',
                                       password='file!?')

    EXPECTED_ENV_CONF = config.Config(username='john.doe@env.com',
                                      password='env!?')

    def test_preconditions(self):
        assert os.path.exists(self.CONFIG_FILE)

    @mock.patch.dict(os.environ,
                     {ENV_PARAM_USER: EXPECTED_ENV_CONF.username, ENV_PARAM_PASSWORD: EXPECTED_ENV_CONF.password})
    def test_environment_variable(self):
        result = config.get_config()
        self.assertEqual(result, self.EXPECTED_ENV_CONF)

    # ensure environment is empty
    @mock.patch.dict(os.environ, {ENV_PARAM_USER: "", ENV_PARAM_PASSWORD: ""})
    def test_file(self):
        # use test file path instead of real one
        config.CONFIG_FILE_PATH = self.CONFIG_FILE

        result = config.get_config()
        self.assertEqual(result, self.EXPECTED_FILE_CONF)

        assert config.get_config() == config.Config(username='john.doe@example.com',
                                                    password='$upersecret')
