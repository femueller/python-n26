import functools
import json
import logging
import os
import re
import unittest
from copy import deepcopy
from unittest import mock
from unittest.mock import Mock, DEFAULT


def read_response_file(file_name: str or None) -> json or None:
    """
    Reads a JSON file and returns it's content as a string
    :param file_name: the name of the file
    :return: file contents
    """

    if file_name is None:
        return None

    import os
    directory = os.path.dirname(__file__)
    file_path = os.path.join(directory, 'api_responses', file_name)

    if not os.path.isfile(file_path):
        raise AttributeError("Couldn't find file containing response mock data: {}".format(file_path))

    with open(file_path, 'r') as myfile:
        api_response_text = myfile.read()
    return json.loads(api_response_text)


def mock_config(username: str = "john.doe@example.com", password: str = "$upersecret", mfa_type: str = "oob"):
    """
    Decorator to mock the configuration.
    This decorator should never be used to test the config itself!

    :param username: the username to use
    :param password: the password to use
    :param mfa_type: the mfa_type to use
    :return: the decorated method
    """

    def decorator(function: callable):
        if not callable(function):
            raise AttributeError("Unsupported type: {}".format(function))

        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            with mock.patch('n26.config.get_config') as mock_config:
                from n26 import config
                mock_config.return_value = config.Config(
                    username=username, password=password,
                    login_data_store_path=None, mfa_type=mfa_type)
                return function(*args, **kwargs)

        return wrapper

    return decorator


def mock_auth_token(func: callable):
    """
    Decorator for mocking the auth token returned by the N26 api

    :param func: function to patch
    :return:
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        with mock.patch('n26.api.Api._request_token') as request_token:
            request_token.return_value = read_response_file("auth_token.json")
            with mock.patch('n26.api.Api._refresh_token') as refresh_token:
                refresh_token.return_value = read_response_file("refresh_token.json")
                return func(*args, **kwargs)

    return wrapper


def mock_requests(method: str, response_file: str or None, url_regex: str = None):
    """
    Decorator to mock the http response

    :param method: the http method to mock
    :param response_file: optional file name of the file containing the json response to use for the mock
    :param url_regex: optional regex to match the called url against. Only matching urls will be mocked.
    :return: the decorated method
    """

    def decorator(function: callable):
        if not callable(function):
            raise AttributeError("Unsupported type: {}".format(function))

        def add_side_effects(mock_request, original):
            new_mock = Mock()

            def side_effect(*args, **kwargs):
                args = deepcopy(args)
                kwargs = deepcopy(kwargs)
                new_mock(*args, **kwargs)

                if not url_regex or re.findall(url_regex, args[0]):
                    return DEFAULT
                else:
                    return original(*args, **kwargs)

            mock_request.side_effect = side_effect

            response = read_response_file(response_file)
            mock_request.return_value.content = "" if response is None else str(response)
            mock_request.return_value.json.return_value = read_response_file(response_file)
            return new_mock

        @mock_auth_token
        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            import n26
            from n26.api import GET, POST
            if method is GET:
                original = n26.api.requests.get
            elif method is POST:
                original = n26.api.requests.post
            else:
                raise AttributeError("Unsupported method: {}".format(method))

            with mock.patch('n26.api.requests.{}'.format(method)) as mock_request:
                add_side_effects(mock_request, original)
                result = function(*args, **kwargs)
                return result

        return wrapper

    return decorator


class N26TestBase(unittest.TestCase):
    """Base class for N26 api tests"""

    PATH = os.path.dirname(os.path.abspath(__file__))
    CONFIG_FILE = os.path.join(PATH, "test_creds.yml")

    # this is the Api client
    _underTest = None

    def setUp(self):
        """
        This method is called BEFORE each individual test case
        """
        from n26 import api, config

        # use test file path instead of real one
        config.CONFIG_FILE_PATH = self.CONFIG_FILE

        self._underTest = api.Api()

        logger = logging.getLogger("n26")
        logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        ch.setFormatter(formatter)
        logger.addHandler(ch)

    def tearDown(self):
        """
        This method is called AFTER each individual test case
        """
        pass

    @staticmethod
    def get_api_response(filename: str) -> dict or None:
        """
        Read an api response from a file

        :param filename: the file in the "api_responses" subfolder to read
        :return: the api response dict
        """
        file = read_response_file(filename)
        if file is None:
            return None
        else:
            return json.loads(file)

    @staticmethod
    def _run_cli_cmd(command: callable, args: list = None, ignore_exceptions: bool = False) -> any:
        """
        Runs a cli command and returns it's output.
        If running the command results in an exception it is automatically rethrown by this method.

        :param command: the command to execute
        :param args: command arguments as a list
        :param ignore_exceptions: if set to true exceptions originating from running the command
                                  will not be rethrown and the result object from the cli call will
                                  be returned instead.
        :return: the result of the call
        """
        from click.testing import CliRunner
        runner = CliRunner(echo_stdin=False)
        result = runner.invoke(command, args=args or ())

        if not ignore_exceptions and result.exception:
            raise result.exception

        return result

    if __name__ == '__main__':
        unittest.main()
