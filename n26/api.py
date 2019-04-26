import time

import requests

from n26 import config
from n26.config import Config

BASE_URL = 'https://api.tech26.de'
BASIC_AUTH_HEADERS = {'Authorization': 'Basic YW5kcm9pZDpzZWNyZXQ='}

GET = "get"
POST = "post"

EXPIRATION_TIME_KEY = "expiration_time"
ACCESS_TOKEN_KEY = "access_token"
REFRESH_TOKEN_KEY = "refresh_token"


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
            cfg = config.get_config()
        self.config = cfg
        self._token_data = {}

    # IDEA: @get_token decorator
    def get_account_info(self) -> dict:
        """
        Retrieves basic account information
        """
        return self._do_request(GET, BASE_URL + '/api/me')

    def get_account_statuses(self) -> dict:
        """
        Retrieves additional account information
        """
        return self._do_request(GET, BASE_URL + '/api/me/statuses')

    def get_addresses(self) -> dict:
        """
        Retrieves a list of addresses of the account owner
        """
        return self._do_request(GET, BASE_URL + '/api/addresses')

    def get_balance(self) -> dict:
        """
        Retrieves the current balance
        """
        return self._do_request(GET, BASE_URL + '/api/accounts')

    def get_spaces(self) -> dict:
        """
        Retrieves a list of all spaces
        """
        return self._do_request(GET, BASE_URL + '/api/spaces')

    def barzahlen_check(self) -> dict:
        return self._do_request(GET, BASE_URL + '/api/barzahlen/check')

    def get_cards(self):
        """
        Retrieves a list of all cards
        """
        return self._do_request(GET, BASE_URL + '/api/v2/cards')

    def get_account_limits(self) -> list:
        """
        Retrieves a list of all active account limits
        """
        return self._do_request(GET, BASE_URL + '/api/settings/account/limits')

    def get_contacts(self):
        """
        Retrieves a list of all contacts
        """
        return self._do_request(GET, BASE_URL + '/api/smrt/contacts')

    def get_standing_orders(self) -> dict:
        """
        Get a list of standing orders
        """
        return self._do_request(GET, BASE_URL + '/api/transactions/so')

    def get_transactions(self, from_time: int = None, to_time: int = None, limit: int = None, pending: bool = None,
                         categories: str = None, text_filter: str = None, last_id: str = None) -> dict:
        """
        Get a list of transactions.

        Note that some parameters can not be combined in a single request (like text_filter and pending) and
        will result in a bad request (400) error.

        :param from_time: earliest transaction time as a Timestamp - milliseconds since 1970 in CET
        :param to_time: latest transaction time as a Timestamp - milliseconds since 1970 in CET
        :param limit: Limit the number of transactions to return to the given amount
        :param pending: show only pending transactions
        :param categories: Comma separated list of category IDs
        :param text_filter: Query string to search for
        :param last_id: ??
        :return: list of transactions
        """
        if pending and limit:
            # pending does not support limit
            limit = None

        return self._do_request(GET, BASE_URL + '/api/smrt/transactions', {
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
        return self._do_request(GET, BASE_URL + '/api/statements')

    def block_card(self, card_id: str) -> dict:
        """
        Blocks a card.
        If the card is already blocked this will have no effect.

        :param card_id: the id of the card to block
        :return: some info about the card (not including it's blocked state... thanks n26!)
        """
        return self._do_request(POST, BASE_URL + '/api/cards/%s/block' % card_id)

    def unblock_card(self, card_id: str) -> dict:
        """
        Unblocks a card.
        If the card is already unblocked this will have no effect.

        :param card_id: the id of the card to block
        :return: some info about the card (not including it's unblocked state... thanks n26!)
        """
        return self._do_request(POST, BASE_URL + '/api/cards/%s/unblock' % card_id)

    def get_savings(self) -> dict:
        return self._do_request(GET, BASE_URL + '/api/hub/savings/accounts')

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

        return self._do_request(GET, BASE_URL + '/api/smrt/statistics/categories/%s/%s' % (from_time, to_time))

    def get_available_categories(self) -> list:
        return self._do_request(GET, BASE_URL + '/api/smrt/categories')

    def get_invitations(self) -> list:
        return self._do_request(GET, BASE_URL + '/api/aff/invitations')

    def _do_request(self, method: str = GET, url: str = "/", params: dict = None) -> list or dict:
        """
        Executes a http request based on the given parameters

        :param method: the method to use (GET, POST)
        :param url: the url to use
        :param params: query parameters that will be appended to the url
        :return: the response parsed as a json
        """
        access_token = self.get_token()
        headers = {'Authorization': 'bearer' + str(access_token)}

        url = self._create_request_url(url, params)

        if method is GET:
            response = requests.get(url, headers=headers)
        elif method is POST:
            response = requests.post(url, headers=headers)
        else:
            raise ValueError("Unsupported method: {}".format(method))

        response.raise_for_status()
        return response.json()

    @staticmethod
    def _create_request_url(url: str, params: dict = None):
        """
        Adds query params to the given url

        :param url: the url to extend
        :param params: query params as a keyed dictionary
        :return: the url including the given query params
        """

        if params:
            first_param = True
            for k, v in sorted(params.items(), key=lambda entry: entry[0]):
                if not v:
                    # skip None values
                    continue

                if first_param:
                    url += '?'
                    first_param = False
                else:
                    url += '&'

                url += "%s=%s" % (k, v)

        return url

    def get_token(self):
        """
        Returns the access token to use for api authentication.
        If a token has been requested before it will be reused if it is still valid.
        If the previous token has expired it will be refreshed.
        If no token has been requested it will be requested from the server.

        :return: the access token
        """
        if not self._validate_token(self._token_data):
            if REFRESH_TOKEN_KEY in self._token_data:
                refresh_token = self._token_data[REFRESH_TOKEN_KEY]
                self._token_data = self._refresh_token(refresh_token)
            else:
                self._token_data = self._request_token(self.config.username, self.config.password)

            # add expiration time to expiration in _validate_token()
            self._token_data[EXPIRATION_TIME_KEY] = time.time() + self._token_data["expires_in"]

        # if it's still not valid, raise an exception
        if not self._validate_token(self._token_data):
            raise PermissionError("Unable to request authentication token")

        return self._token_data[ACCESS_TOKEN_KEY]

    @staticmethod
    def _request_token(username: str, password: str):
        """
        Request an authentication token from the server
        :return: the token or None if the response did not contain a token
        """
        values_token = {
            'grant_type': 'password',
            'username': username,
            'password': password
        }

        response = requests.post(BASE_URL + '/oauth/token', data=values_token, headers=BASIC_AUTH_HEADERS)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def _refresh_token(refresh_token: str):
        """
        Refreshes an authentication token
        :param refresh_token: the refresh token issued by the server when requesting a token
        :return: the refreshed token data
        """
        values_token = {
            'grant_type': REFRESH_TOKEN_KEY,
            'refresh_token': refresh_token
        }

        response = requests.post(BASE_URL + '/oauth/token', data=values_token, headers=BASIC_AUTH_HEADERS)
        response.raise_for_status()
        return response.json()

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
