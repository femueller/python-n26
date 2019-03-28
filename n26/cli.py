import n26.api as api
import click
import webbrowser
from tabulate import tabulate

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


# Cli returns command line requests
@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    """Interact with the https://n26.com API via the command line."""


client = api.Api()


@cli.command()
def info():
    """ Get account information """
    account_info = client.get_account_info()

    # TODO: make it python2 compatible using unicode
    text = """
    Account info:
    -------------
    Name: %s %s
    Email: %s
    Nationality: %s
    Phone: %s
    """ % (account_info['firstName'],
           account_info['lastName'],
           account_info['email'],
           account_info['nationality'],
           account_info['mobilePhoneNumber']
           )

    print(text.strip())


@cli.command()
def balance():
    """ Show account balance """
    print('Current balance:')
    print('----------------')
    print(str(client.get_balance()['availableBalance']))


@cli.command()
def browse():
    """ Browse on the web https://app.n26.com/ """
    webbrowser.open('https://app.n26.com/')


@cli.command()
def spaces():
    """ Show spaces """
    print('Spaces:')
    print('----------------')
    for space in client.get_spaces():
        balance = space['balance']['availableBalance']
        string = str(space['name']) + ': ' + str(balance)
        if 'goal' in space:
            goal = space['goal']['amount']
            percentage = balance / goal
            string += '/' + str(goal) + ' <- ' + '{:.2%}'.format(percentage)
        print(string)


@cli.command()
# @click.option('--all', default=False, help='Blocks all n26 cards.')
def card_block():
    """ Blocks the card. """
    for card in client.get_cards():
        card_id = card['id']
        client.block_card(card_id)
        print('Blocked card: ' + card_id)


@cli.command()
def card_unblock():
    """ Unblocks the card. """
    for card in client.get_cards():
        card_id = card['id']
        client.unblock_card(card_id)
        print('Unblocked card: ' + card_id)


@cli.command()
def limits():
    """ Show n26 account limits  """
    print(client.get_account_limits())


@cli.command()
def contacts():
    """ Show your n26 contacts  """
    print('Contacts:')
    print('---------')
    print(client.get_contacts())


@cli.command()
def statements():
    """ Show your n26 statements  """
    print('Statements:')
    print('-----------')
    print(client.get_statements())


@cli.command()
@click.option('--limit', default=5, type=click.IntRange(1, 10000), help='Limit transaction output.')
def transactions(limit):
    """ Show transactions (default: 5) """
    output = client.get_transactions(limit=limit)
    print('Transactions:')
    print('-------------')
    li = []
    for i, val in enumerate(output):
        try:
            if val['merchantName'] in val.values():
                li.append([i, str(val['amount']), val['merchantName']])
        except KeyError:
            if val['referenceText'] in val.values():
                li.append([i, str(val['amount']), val['referenceText']])
            else:
                li.append([i, str(val['amount']), 'no details available'])

    # Tabulate
    table = li
    headers = ['index', 'amount', 'details']
    print(tabulate(table, headers, tablefmt='simple', numalign='right'))


if __name__ == '__main__':
    cli()
