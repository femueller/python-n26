import functools
import json
import unittest
from unittest import mock

from n26 import api


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


def mock_api(method: str, response_file: str = None):
    """
    Decorator to mock the http response

    :param method: the method to decorate
    :param response_file: the file name of the file containing the json response to use for the mock
    :return: the decorated method
    """

    def decorator(function):
        if not callable(function):
            raise AttributeError("Unsupported type: {}".format(function))

        @mock_auth_token
        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            with mock.patch('n26.api.requests.{}'.format(method)) as mock_post:
                mock_post.return_value.json.return_value = read_response_file(response_file)
                result = function(*args, **kwargs)
                return result

        return wrapper

    return decorator


class N26TestBase(unittest.TestCase):
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
