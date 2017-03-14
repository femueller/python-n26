import n26.api as api
import click


# Cli returns command line requests
@click.group()
def cli():
    """Interact with the https://n26.com API via the command line."""


@cli.command()
def info():
    """ Get account information """
    account_info = api.Api()
    print('Account info:')
    print('-------------')
    # TODO: make it python2 compatible using unicode
    print('Name: ' + str(account_info.get_account_info()['firstName'] + ' ' + account_info.get_account_info()['lastName']))
    print('Email: ' + account_info.get_account_info()['email'])
    print('Nationality: ' + account_info.get_account_info()['nationality'])
    print('Phone: ' + account_info.get_account_info()['mobilePhoneNumber'])


@cli.command()
def balance():
    """ Show account balance """
    balance = api.Api()
    print('Current balance:')
    print('----------------')
    print(str(balance.get_balance()['availableBalance']))
    # print(balance.get_balance())


@cli.command()
def cards():
    """ Show your n26 cards  """
    cards = api.Api()
    print(cards.get_cards())


@cli.command()
def contacts():
    """ Show your n26 contacts  """
    contacts = api.Api()
    print('Contacts:')
    print('---------')
    print(contacts.get_contacts())


@cli.command()
def statements():
    """ Show your n26 statements  """
    statements = api.Api()
    print('Statements:')
    print('-----------')
    print(statements.get_statements())


@cli.command()
def transactions():
    """ Show transactions  """
    transactions = api.Api()
    print('Transactions:')
    print('-------------')
    # print(transactions.get_transactions())
    print(transactions.get_transactions())


if __name__ == '__main__':
    cli()
