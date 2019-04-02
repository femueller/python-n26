import functools
import json
import re
import unittest
from copy import deepcopy
from unittest import mock
from unittest.mock import Mock, DEFAULT

import n26
from n26 import api
from n26.api import GET, POST


def read_response_file(file_name: str) -> str:
    """
    Reads a JSON file and returns it's content as a string
    :param file_name: the name of the file
    :return: file contents
    """

    import os
    directory = os.path.dirname(__file__)
    file_path = os.path.join(directory, 'api_responses', file_name)

    if not os.path.isfile(file_path):
        raise AttributeError("Couldn't find file: {}".format(file_path))

    with open(file_path, 'r') as myfile:
        api_response_text = myfile.read()
    return json.loads(api_response_text)


def mock_auth_token(func):
    """
    Decorator for mocking the auth token returned by the N26 api

    :param func: function to patch
    :return:
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        with mock.patch('n26.api.Api._request_token') as mock_token:
            mock_token.return_value = read_response_file("auth_token.json")
            return func(*args, **kwargs)

    return wrapper


def mock_api(method: str, response_file: str, url_regex: str = None):
    """
    Decorator to mock the http response

    :param url_regex: a regex to match the called url against. Only matching urls will be mocked.
    :param method: the method to decorate
    :param response_file: the file name of the file containing the json response to use for the mock
    :return: the decorated method
    """

    def decorator(function):
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
            mock_request.return_value.json.return_value = read_response_file(response_file)
            return new_mock

        @mock_auth_token
        @functools.wraps(function)
        def wrapper(*args, **kwargs):
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

    # this is the Api client
    _underTest = None

    def setUp(self):
        self._underTest = api.Api()

    def tearDown(self):
        pass

    @staticmethod
    def get_api_response(filename: str) -> dict:
        """
        Read an api response from a file

        :param filename: the file in the "api_responses" subfolder to read
        :return: the hypothetical api response dict to use as a replacement for the "send_request" method
        """

        import os
        directory = os.path.dirname(__file__)
        file_path = os.path.join(directory, 'api_responses', filename)

        with open(file_path, 'r') as myfile:
            api_response_text = myfile.read()
        return json.loads(api_response_text)

    if __name__ == '__main__':
        unittest.main()
