import json
import logging
import os
import time
from pathlib import Path

import click
import requests
from requests import HTTPError
from tenacity import retry, stop_after_delay, wait_fixed

from n26.config import Config, MFA_TYPE_SMS
from n26.const import DAILY_WITHDRAWAL_LIMIT, DAILY_PAYMENT_LIMIT
from n26.util import create_request_url

LOGGER = logging.getLogger(__name__)

BASE_URL_DE = 'https://api.tech26.de'
BASE_URL_GLOBAL = 'https://api.tech26.global'
BASIC_AUTH_HEADERS = {"Authorization": "Basic bXktdHJ1c3RlZC13ZHBDbGllbnQ6c2VjcmV0"}
USER_AGENT = ("Mozilla/5.0 (X11; Linux x86_64) "
              "AppleWebKit/537.36 (KHTML, like Gecko) "
              "Chrome/59.0.3071.86 Safari/537.36")

GET = "get"
POST = "post"

EXPIRATION_TIME_KEY = "expiration_time"
ACCESS_TOKEN_KEY = "access_token"
REFRESH_TOKEN_KEY = "refresh_token"

GRANT_TYPE_PASSWORD = "password"
GRANT_TYPE_REFRESH_TOKEN = "refresh_token"


class Api(object):
    """
    Api class can be imported as a library in order to use it within applications
    """

    def __init__(self, cfg: Config = None):
        """
        Constructor accepting None to maintain backward compatibility

        :param cfg: configuration object
        """
        if not cfg:
            cfg = Config()
        self.config = cfg
        self._token_data = {}

    @property
    def token_data(self) -> dict:
        if self.config.LOGIN_DATA_STORE_PATH.value is None:
            return self._token_data
        else:
            return self._read_token_file(self.config.LOGIN_DATA_STORE_PATH.value)

    @token_data.setter
    def token_data(self, data: dict):
        if self.config.LOGIN_DATA_STORE_PATH.value is None:
            self._token_data = data
        else:
            self._write_token_file(data, self.config.LOGIN_DATA_STORE_PATH.value)

    @staticmethod
    def _read_token_file(path: str) -> dict:
        """
        :return: the stored token data or an empty dict
        """
        LOGGER.debug("Reading token data from {}".format(path))
        path = Path(path).expanduser().resolve()
        if not path.exists():
            return {}

        if not path.is_file():
            raise IsADirectoryError("File path exists and is not a file: {}".format(path))

        if path.stat().st_size <= 0:
            # file is empty
            return {}

        with open(path, "r") as file:
            return json.loads(file.read())

    @staticmethod
    def _write_token_file(token_data: dict, path: str):
        LOGGER.debug("Writing token data to {}".format(path))
        path = Path(path).expanduser().resolve()

        # delete existing file if permissions don't match or file size is abnormally small
        if path.exists() and (path.stat().st_mode != 0o100600 or path.stat().st_size < 10):
            path.unlink()

        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        with os.fdopen(os.open(path, os.O_WRONLY | os.O_CREAT, 0o600), 'w') as file:
            file.seek(0)
            file.write(json.dumps(token_data, indent=2))
            file.truncate()

    # IDEA: @get_token decorator
    def get_account_info(self) -> dict:
        """
        Retrieves basic account information
        """
        return self._do_request(GET, BASE_URL_DE + '/api/me')

    def get_account_statuses(self) -> dict:
        """
        Retrieves additional account information
        """
        return self._do_request(GET, BASE_URL_DE + '/api/me/statuses')

    def get_addresses(self) -> dict:
        """
        Retrieves a list of addresses of the account owner
        """
        return self._do_request(GET, BASE_URL_DE + '/api/addresses')

    def get_balance(self) -> dict:
        """
        Retrieves the current balance
        """
        return self._do_request(GET, BASE_URL_DE + '/api/accounts')

    def get_spaces(self) -> dict:
        """
        Retrieves a list of all spaces
        """
        return self._do_request(GET, BASE_URL_DE + '/api/spaces')

    def barzahlen_check(self) -> dict:
        return self._do_request(GET, BASE_URL_DE + '/api/barzahlen/check')

    def get_cards(self):
        """
        Retrieves a list of all cards
        """
        return self._do_request(GET, BASE_URL_DE + '/api/v2/cards')

    def get_account_limits(self) -> list:
        """
        Retrieves a list of all active account limits
        """
        return self._do_request(GET, BASE_URL_DE + '/api/settings/account/limits')

    def set_account_limits(self, daily_withdrawal_limit: int = None, daily_payment_limit: int = None) -> None:
        """
        Sets account limits

        :param daily_withdrawal_limit: daily withdrawal limit
        :param daily_payment_limit: daily payment limit
        """
        if daily_withdrawal_limit is not None:
            self._do_request(POST, BASE_URL_DE + '/api/settings/account/limits', json={
                "limit": DAILY_WITHDRAWAL_LIMIT,
                "amount": daily_withdrawal_limit
            })

        if daily_payment_limit is not None:
            self._do_request(POST, BASE_URL_DE + '/api/settings/account/limits', json={
                "limit": DAILY_PAYMENT_LIMIT,
                "amount": daily_payment_limit
            })

    def get_contacts(self):
        """
        Retrieves a list of all contacts
        """
        return self._do_request(GET, BASE_URL_DE + '/api/smrt/contacts')

    def get_standing_orders(self) -> dict:
        """
        Get a list of standing orders
        """
        return self._do_request(GET, BASE_URL_DE + '/api/transactions/so')

    def get_transactions(self, from_time: int = None, to_time: int = None, limit: int = 20, pending: bool = None,
                         categories: str = None, text_filter: str = None, last_id: str = None) -> dict:
        """
        Get a list of transactions.

        Note that some parameters can not be combined in a single request (like text_filter and pending) and
        will result in a bad request (400) error.

        :param from_time: earliest transaction time as a Timestamp > 0 - milliseconds since 1970 in CET
        :param to_time: latest transaction time as a Timestamp > 0 - milliseconds since 1970 in CET
        :param limit: Limit the number of transactions to return to the given amount - default 20 as the n26 API returns
        only the last 20 transactions by default
        :param pending: show only pending transactions
        :param categories: Comma separated list of category IDs
        :param text_filter: Query string to search for
        :param last_id: ??
        :return: list of transactions
        """
        if pending and limit:
            # pending does not support limit
            limit = None

        return self._do_request(GET, BASE_URL_DE + '/api/smrt/transactions', {
            'from': from_time,
            'to': to_time,
            'limit': limit,
            'pending': pending,
            'categories': categories,
            'textFilter': text_filter,
            'lastId': last_id
        })

    def get_transactions_limited(self, limit: int = 5) -> dict:
        import warnings
        warnings.warn(
            "get_transactions_limited is deprecated, use get_transactions(limit=5) instead",
            DeprecationWarning
        )
        return self.get_transactions(limit=limit)

    def get_statements(self) -> list:
        """
        Retrieves a list of all statements
        """
        return self._do_request(GET, BASE_URL_DE + '/api/statements')

    def block_card(self, card_id: str) -> dict:
        """
        Blocks a card.
        If the card is already blocked this will have no effect.

        :param card_id: the id of the card to block
        :return: some info about the card (not including it's blocked state... thanks n26!)
        """
        return self._do_request(POST, BASE_URL_DE + '/api/cards/%s/block' % card_id)

    def unblock_card(self, card_id: str) -> dict:
        """
        Unblocks a card.
        If the card is already unblocked this will have no effect.

        :param card_id: the id of the card to block
        :return: some info about the card (not including it's unblocked state... thanks n26!)
        """
        return self._do_request(POST, BASE_URL_DE + '/api/cards/%s/unblock' % card_id)

    def get_savings(self) -> dict:
        return self._do_request(GET, BASE_URL_DE + '/api/hub/savings/accounts')

    def get_statistics(self, from_time: int = 0, to_time: int = int(time.time()) * 1000) -> dict:
        """
        Get statistics in a given time frame

        :param from_time: Timestamp - milliseconds since 1970 in CET
        :param to_time: Timestamp - milliseconds since 1970 in CET
        """

        if not from_time:
            from_time = 0

        if not to_time:
            to_time = int(time.time()) * 1000

        return self._do_request(GET, BASE_URL_DE + '/api/smrt/statistics/categories/%s/%s' % (from_time, to_time))

    def get_available_categories(self) -> list:
        return self._do_request(GET, BASE_URL_DE + '/api/smrt/categories')

    def get_invitations(self) -> list:
        return self._do_request(GET, BASE_URL_DE + '/api/aff/invitations')

    def _do_request(self, method: str = GET, url: str = "/", params: dict = None,
                    json: dict = None) -> list or dict or None:
        """
        Executes a http request based on the given parameters

        :param method: the method to use (GET, POST)
        :param url: the url to use
        :param params: query parameters that will be appended to the url
        :param json: request body
        :return: the response parsed as a json
        """
        access_token = self.get_token()
        headers = {'Authorization': 'Bearer {}'.format(access_token)}

        url = create_request_url(url, params)

        if method is GET:
            response = requests.get(url, headers=headers, json=json)
        elif method is POST:
            response = requests.post(url, headers=headers, json=json)
        else:
            raise ValueError("Unsupported method: {}".format(method))

        response.raise_for_status()
        # some responses do not return data so we just ignore the body in that case
        if len(response.content) > 0:
            return response.json()

    def is_authenticated(self) -> bool:
        """
        :return: whether valid token data exists
        """
        return self._validate_token(self.token_data)

    def authenticate(self):
        """
        Starts a new authentication flow with the N26 servers.

        This method requires user interaction to approve a 2FA request.
        Therefore you should make sure if you can bypass this
        by refreshing or reusing an existing token by calling is_authenticated()
        and refresh_authentication() respectively.

        :raises PermissionError: if the token is invalid even after the refresh
        """
        LOGGER.debug("Requesting token for username: {}".format(self.config.USERNAME.value))
        token_data = self._request_token(self.config.USERNAME.value, self.config.PASSWORD.value)

        # add expiration time to expiration in _validate_token()
        token_data[EXPIRATION_TIME_KEY] = time.time() + token_data["expires_in"]

        # if it's still not valid, raise an exception
        if not self._validate_token(token_data):
            raise PermissionError("Unable to request authentication token")

        # save token data
        self.token_data = token_data

    def refresh_authentication(self):
        """
        Refreshes an existing authentication using a (possibly expired) token.
        :raises AssertionError: if no existing token data was found
        :raises PermissionError: if the token is invalid even after the refresh
        """
        token_data = self.token_data
        if REFRESH_TOKEN_KEY in token_data:
            LOGGER.debug("Trying to refresh existing token")
            refresh_token = token_data[REFRESH_TOKEN_KEY]
            token_data = self._refresh_token(refresh_token)
        else:
            raise AssertionError("Cant refresh token since no existing token data was found. "
                                 "Please initiate a new authentication instead.")

        # add expiration time to expiration in _validate_token()
        token_data[EXPIRATION_TIME_KEY] = time.time() + token_data["expires_in"]

        # if it's still not valid, raise an exception
        if not self._validate_token(token_data):
            raise PermissionError("Unable to refresh authentication token")

        # save token data
        self.token_data = token_data

    def get_token(self):
        """
        Returns the access token to use for api authentication.
        If a token has been requested before it will be reused if it is still valid.
        If the previous token has expired it will be refreshed.
        If no token has been requested it will be requested from the server.

        :return: the access token
        """
        new_auth = False
        if not self._validate_token(self.token_data):
            try:
                self.refresh_authentication()
            except HTTPError as http_error:
                if http_error.response.status_code != 401:
                    raise http_error
                new_auth = True
            except AssertionError:
                new_auth = True

        if new_auth:
            self.authenticate()

        return self.token_data[ACCESS_TOKEN_KEY]

    def _request_token(self, username: str, password: str):
        """
        Request an authentication token from the server
        :return: the token or None if the response did not contain a token
        """
        mfa_token = self._initiate_authentication_flow(username, password)
        self._request_mfa_approval(mfa_token)
        return self._complete_authentication_flow(mfa_token)

    @staticmethod
    def _initiate_authentication_flow(username: str, password: str) -> str:
        LOGGER.debug("Requesting authentication flow for user {}".format(username))
        values_token = {
            "grant_type": GRANT_TYPE_PASSWORD,
            "username": username,
            "password": password
        }
        # TODO: Seems like the user-agent is not necessary but might be a good idea anyway
        response = requests.post(BASE_URL_GLOBAL + "/oauth/token", data=values_token, headers=BASIC_AUTH_HEADERS)
        if response.status_code != 403:
            raise ValueError("Unexpected response for initial auth request: {}".format(response.text))

        response_data = response.json()
        if response_data.get("error", "") == "mfa_required":
            return response_data["mfaToken"]
        else:
            raise ValueError("Unexpected response data")

    @staticmethod
    def _refresh_token(refresh_token: str):
        """
        Refreshes an authentication token
        :param refresh_token: the refresh token issued by the server when requesting a token
        :return: the refreshed token data
        """
        LOGGER.debug("Requesting token refresh using refresh_token {}".format(refresh_token))
        values_token = {
            'grant_type': GRANT_TYPE_REFRESH_TOKEN,
            'refresh_token': refresh_token,
        }

        response = requests.post(BASE_URL_GLOBAL + '/oauth/token', data=values_token, headers=BASIC_AUTH_HEADERS)
        response.raise_for_status()
        return response.json()

    def _request_mfa_approval(self, mfa_token: str):
        LOGGER.debug("Requesting MFA approval using mfa_token {}".format(mfa_token))
        mfa_data = {
            "mfaToken": mfa_token
        }

        if self.config.MFA_TYPE.value == MFA_TYPE_SMS:
            mfa_data['challengeType'] = "otp"
        else:
            mfa_data['challengeType'] = "oob"

        response = requests.post(
            BASE_URL_DE + "/api/mfa/challenge",
            json=mfa_data,
            headers={
                **BASIC_AUTH_HEADERS,
                "User-Agent": USER_AGENT,
                "Content-Type": "application/json"
            })
        response.raise_for_status()

    @retry(wait=wait_fixed(5), stop=stop_after_delay(60))
    def _complete_authentication_flow(self, mfa_token: str) -> dict:
        LOGGER.debug("Completing authentication flow for mfa_token {}".format(mfa_token))
        mfa_response_data = {
            "mfaToken": mfa_token
        }

        if self.config.MFA_TYPE.value == MFA_TYPE_SMS:
            mfa_response_data['grant_type'] = "mfa_otp"

            hint = click.style("Enter the 6 digit SMS OTP code", fg="yellow")
            mfa_response_data['otp'] = click.prompt(hint, type=int)
        else:
            mfa_response_data['grant_type'] = "mfa_oob"

        response = requests.post(BASE_URL_DE + "/oauth/token", data=mfa_response_data, headers=BASIC_AUTH_HEADERS)
        response.raise_for_status()
        tokens = response.json()
        return tokens

    @staticmethod
    def _validate_token(token_data: dict):
        """
        Checks if a token is valid
        :param token_data: the token data to check
        :return: true if valid, false otherwise
        """
        if EXPIRATION_TIME_KEY not in token_data:
            # there was a problem adding the expiration_time property
            return False
        elif time.time() >= token_data[EXPIRATION_TIME_KEY]:
            # token has expired
            return False

        return ACCESS_TOKEN_KEY in token_data and token_data[ACCESS_TOKEN_KEY]
