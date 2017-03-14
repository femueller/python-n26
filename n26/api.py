import requests
import n26.config as config

url = 'https://api.tech26.de'


# Api class can be imported as a library in order to use it within applications
class Api():
    def get_token(self):
        values_token = {'grant_type': 'password', 'username': config.username, 'password': config.password}
        headers_token = {'Authorization': 'Basic YW5kcm9pZDpzZWNyZXQ='}

        response_token = requests.post(url + '/oauth/token', data=values_token, headers=headers_token)
        token_info = response_token.json()
        # TODO check if access_token is not nil
        return token_info['access_token']

    def get_account_info(get_token):
        token_api = Api()
        access_token = token_api.get_token()
        headers_balance = {'Authorization': 'bearer' + str(access_token)}
        req_account_info = requests.get(url + '/api/me', headers=headers_balance)
        info = req_account_info.json()
        return info

    def get_addresses(get_token):
        token_api = Api()
        access_token = token_api.get_token()
        headers_balance = {'Authorization': 'bearer' + str(access_token)}
        req_addresses = requests.get(url + '/api/addresses', headers=headers_balance)
        addresses = req_addresses.json()
        return addresses

    def get_balance(get_token):
        token_api = Api()
        access_token = token_api.get_token()
        headers_balance = {'Authorization': 'bearer' + str(access_token)}
        req_balance = requests.get(url + '/api/accounts', headers=headers_balance)
        balance = req_balance.json()
        return balance

    def get_cards(get_token):
        token_api = Api()
        access_token = token_api.get_token()
        headers_balance = {'Authorization': 'bearer' + str(access_token)}
        req_cards = requests.get(url + '/api/cards', headers=headers_balance)
        cards = req_cards.json()
        return cards

    def get_contacts(get_token):
        token_api = Api()
        access_token = token_api.get_token()
        headers_balance = {'Authorization': 'bearer' + str(access_token)}
        req_contacts = requests.get(url + '/api/smrt/contacts', headers=headers_balance)
        contacts = req_contacts.json()
        return contacts

    def get_transactions(get_token):
        token_api = Api()
        access_token = token_api.get_token()
        headers_balance = {'Authorization': 'bearer' + str(access_token)}
        req_transactions = requests.get(url + '/api/smrt/transactions', headers=headers_balance)
        transactions = req_transactions.json()
        return transactions

    def get_statements(get_token):
        token_api = Api()
        access_token = token_api.get_token()
        headers_balance = {'Authorization': 'bearer' + str(access_token)}
        req_statements = requests.get(url + '/api/statements', headers=headers_balance)
        statements = req_statements.json()
        return statements

    # TODO: This method should enable a transfer
    # https://github.com/PierrickP/n26/blob/develop/lib/account.js#L620-L632
    def make_transfer(pin, iban, bic, name, amount, reference):
        pass

    def block_card(get_token, card_id):
        token_api = Api()
        access_token = token_api.get_token()
        headers_balance = {'Authorization': 'bearer' + str(access_token)}
        req_transactions = requests.post(url + 'api/cards/' + card_id + '/block', headers=headers_balance)
        transactions = req_transactions.json()
        return transactions

    def unblock_card(get_token, card_id):
        token_api = Api()
        access_token = token_api.get_token()
        headers_balance = {'Authorization': 'bearer' + str(access_token)}
        req_transactions = requests.post(url + 'api/cards/' + card_id + '/unblock', headers=headers_balance)
        transactions = req_transactions.json()
        return transactions
