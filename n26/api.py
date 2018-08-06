import requests
from n26 import config

url = 'https://api.tech26.de'


# Api class can be imported as a library in order to use it within applications
class Api(object):
    # constructor accepting None to maintain backward compatibility
    def __init__(self, cfg=None):
        if not cfg:
            cfg = config.get_config()
        self.config = cfg

    def get_token(self):
        values_token = {'grant_type': 'password', 'username': self.config.username, 'password': self.config.password}
        headers_token = {'Authorization': 'Basic YW5kcm9pZDpzZWNyZXQ='}

        response_token = requests.post(url + '/oauth/token', data=values_token, headers=headers_token)
        token_info = response_token.json()
        # TODO check if access_token is not nil
        return token_info['access_token']

    # TODO: this method will check if token is valid, if not it will run get_token
    def validate_token():
        pass

    # IDEA: @get_token decorator
    def get_account_info(self):
        access_token = self.get_token()
        headers_balance = {'Authorization': 'bearer' + str(access_token)}
        req_account_info = requests.get(url + '/api/me', headers=headers_balance)
        info = req_account_info.json()
        return info

    def get_account_statuses(self):
        access_token = self.get_token()
        headers_balance = {'Authorization': 'bearer' + str(access_token)}
        req_account_statuses = requests.get(url + '/api/me/statuses', headers=headers_balance)
        status = req_account_statuses.json()
        return status

    def get_addresses(self):
        access_token = self.get_token()
        headers_balance = {'Authorization': 'bearer' + str(access_token)}
        req_addresses = requests.get(url + '/api/addresses', headers=headers_balance)
        addresses = req_addresses.json()
        return addresses

    def get_balance(self):
        access_token = self.get_token()
        headers_balance = {'Authorization': 'bearer' + str(access_token)}
        req_balance = requests.get(url + '/api/accounts', headers=headers_balance)
        balance = req_balance.json()
        return balance

    def barzahlen_check(self):
        access_token = self.get_token()
        headers_balance = {'Authorization': 'bearer' + str(access_token)}
        req_barzahlen_check = requests.get(url + '/api/barzahlen/check', headers=headers_balance)
        barzahlen_check = req_barzahlen_check.json()
        return barzahlen_check

    def get_cards(self):
        access_token = self.get_token()
        headers_balance = {'Authorization': 'bearer' + str(access_token)}
        req_cards = requests.get(url + '/api/v2/cards', headers=headers_balance)
        cards = req_cards.json()
        return cards

    def get_account_limits(self):
        access_token = self.get_token()
        headers_balance = {'Authorization': 'bearer' + str(access_token)}
        req_limits = requests.get(url + '/api/settings/account/limits', headers=headers_balance)
        limits = req_limits.json()
        return limits

    def get_contacts(self):
        access_token = self.get_token()
        headers_balance = {'Authorization': 'bearer' + str(access_token)}
        req_contacts = requests.get(url + '/api/smrt/contacts', headers=headers_balance)
        contacts = req_contacts.json()
        return contacts

    def get_transactions(self):
        access_token = self.get_token()
        headers_balance = {'Authorization': 'bearer' + str(access_token)}
        req_transactions = requests.get(url + '/api/smrt/transactions', headers=headers_balance)
        transactions = req_transactions.json()
        return transactions

    def get_transactions_limited(self, limit=5):
        access_token = self.get_token()
        headers_balance = {'Authorization': 'bearer' + str(access_token)}
        req_transactions = requests.get(url + '/api/smrt/transactions?limit=' +
                                        str(limit), headers=headers_balance)
        transactions = req_transactions.json()
        return transactions

    def get_statements(self):
        access_token = self.get_token()
        headers_balance = {'Authorization': 'bearer' + str(access_token)}
        req_statements = requests.get(url + '/api/statements', headers=headers_balance)
        statements = req_statements.json()
        return statements

    def block_card(self, card_id):
        access_token = self.get_token()
        headers_balance = {'Authorization': 'bearer' + str(access_token)}
        req_block_card = requests.post(url + '/api/cards/' + card_id + '/block', headers=headers_balance)
        blocked_card = req_block_card.json()
        return blocked_card

    def unblock_card(self, card_id):
        access_token = self.get_token()
        headers_balance = {'Authorization': 'bearer' + str(access_token)}
        req_unblock_card = requests.post(url + '/api/cards/' + card_id + '/unblock', headers=headers_balance)
        unblocked_card = req_unblock_card.json()
        return unblocked_card
