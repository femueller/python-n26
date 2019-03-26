import textwrap

import n26.api as api
import click
import webbrowser
from tabulate import tabulate

API_CLIENT = api.Api()

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


# Cli returns command line requests
@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    """Interact with the https://n26.com API via the command line."""


@cli.command()
def info():
    """ Get account information """
    account_info = API_CLIENT.get_account_info()

    lines = [
        ["Name:", "%s %s" % (account_info['firstName'], account_info['lastName'])],
        ["Email:", account_info['email']],
        ["Nationality:", account_info['nationality']],
        ["Phone:", account_info['mobilePhoneNumber']]
    ]

    text = tabulate(lines, [], tablefmt="plain", colalign=["right", "left"])

    click.echo(text)


@cli.command()
def balance():
    """ Show account balance """
    balance_data = API_CLIENT.get_balance()
    amount = balance_data.get('availableBalance')
    currency = balance_data.get('currency')
    click.echo("%s %s" % (amount, currency))


@cli.command()
def browse():
    """ Browse on the web https://app.n26.com/ """
    webbrowser.open('https://app.n26.com/')


@cli.command()
def spaces():
    """ Show spaces """
    spaces_data = API_CLIENT.get_spaces()["spaces"]

    lines = []
    for i, space in enumerate(spaces_data):
        line = []
        available_balance = space['balance']['availableBalance']
        currency = space['balance']['currency']
        name = space['name']

        line.append(name)
        line.append("%s %s" % (available_balance, currency))

        if 'goal' in space:
            goal = space['goal']['amount']
            percentage = available_balance / goal

            line.append("%s %s" % (goal, currency))
            line.append('{:.2%}'.format(percentage))

        lines.append(line)

    headers = ['Name', 'Balance', 'Goal', 'Progress']
    text = tabulate(lines, headers, colalign=['left', 'right', 'right', 'right'], numalign='right')

    click.echo(text)


@cli.command()
# @click.option('--all', default=False, help='Blocks all n26 cards.')
def card_block():
    """ Blocks the card. """
    for card in API_CLIENT.get_cards():
        card_id = card['id']
        API_CLIENT.block_card(card_id)
        click.echo('Blocked card: ' + card_id)


@cli.command()
def card_unblock():
    """ Unblocks the card. """
    for card in API_CLIENT.get_cards():
        card_id = card['id']
        API_CLIENT.unblock_card(card_id)
        click.echo('Unblocked card: ' + card_id)


@cli.command()
def limits():
    """ Show n26 account limits  """
    limits_data = API_CLIENT.get_account_limits()

    lines = []
    for limit in limits_data:
        name = limit["limit"]
        amount = limit["amount"]
        countries = limit["countryList"]

        lines.append([name, amount, countries])

    headers = ['Name', 'Amount', 'Country List']
    text = tabulate(lines, headers, numalign='right')

    click.echo(text)


@cli.command()
def contacts():
    """ Show your n26 contacts  """

    contacts_data = API_CLIENT.get_contacts()

    headers = ['Id', 'Name', 'Subtitle']
    lines = [
        list(x.values())[1:-1]
        for x in contacts_data
    ]
    text = tabulate(lines, headers, numalign='right')

    click.echo(text.strip())


@cli.command()
def statements():
    """ Show your n26 statements  """
    statements_data = API_CLIENT.get_statements()

    headers = ['Id', 'Url', 'Visible TS', 'Month', 'Year']
    lines = [
        list(x.values())
        for x in statements_data
    ]
    text = tabulate(lines, headers, numalign='right')

    click.echo(text.strip())


@cli.command()
@click.option('--limit', default=5, type=click.IntRange(1, 10000), help='Limit transaction output.')
def transactions(limit):
    """ Show transactions (default: 5) """
    output = API_CLIENT.get_transactions(limit=limit)

    text = "Transactions:\n"
    text += "-------------\n"

    lines = []
    for i, val in enumerate(output):
        try:
            if val['merchantName'] in val.values():
                lines.append([i, str(val['amount']), val['merchantName']])
        except KeyError:
            if val['referenceText'] in val.values():
                lines.append([i, str(val['amount']), val['referenceText']])
            else:
                lines.append([i, str(val['amount']), 'no details available'])

    headers = ['index', 'amount', 'details']
    text += tabulate(lines, headers, numalign='right')

    click.echo(text.strip())


if __name__ == '__main__':
    statements()
    cli()
