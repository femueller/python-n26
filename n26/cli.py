import webbrowser
from datetime import datetime, timezone

import click
from tabulate import tabulate

import n26.api as api

API_CLIENT = api.Api()

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


# Cli returns command line requests
@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    """Interact with the https://n26.com API via the command line."""


client = api.Api()


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
        else:
            line.append("-")
            line.append("-")

        lines.append(line)

    headers = ['Name', 'Balance', 'Goal', 'Progress']
    text = tabulate(lines, headers, colalign=['left', 'right', 'right', 'right'], numalign='right')

    click.echo(text)


@cli.command()
@click.option('--card', default=None, type=str, help='ID of the card to block. Omitting this will block all cards.')
def card_block(card):
    """ Blocks the card/s """
    if card:
        card_ids = [card]
    else:
        card_ids = [card['id'] for card in API_CLIENT.get_cards()]

    for card_id in card_ids:
        API_CLIENT.block_card(card_id)
        click.echo('Blocked card: ' + card_id)


@cli.command()
@click.option('--card', default=None, type=str, help='ID of the card to unblock. Omitting this will unblock all cards.')
def card_unblock(card):
    """ Unblocks the card/s """
    if card:
        card_ids = [card]
    else:
        card_ids = [card['id'] for card in API_CLIENT.get_cards()]

    for card_id in card_ids:
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
    transactions_data = API_CLIENT.get_transactions(limit=limit)

    text = "Transactions:\n"
    text += "-------------\n"

    lines = []
    for i, val in enumerate(transactions_data):
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


@cli.command()
@click.option('--from', 'param_from', default=None, type=int,
              help='Start time limit for statistics. Timestamp - milliseconds since 1970 in CET')
@click.option('--to', default=None, type=int,
              help='End time limit for statistics. Timestamp - milliseconds since 1970 in CET')
def statistics(param_from, to):
    """Show your n26 statistics"""
    statements_data = API_CLIENT.get_statistics(from_time=param_from, to_time=to)

    text = "From: %s\n" % (_timestamp_ms_to_date(statements_data["from"]))
    text += "To:   %s\n\n" % (_timestamp_ms_to_date(statements_data["to"]))

    lines = []
    total = statements_data["total"]
    total_income = statements_data["totalIncome"]
    total_expense = statements_data["totalExpense"]

    income_items = statements_data["incomeItems"]
    expense_items = statements_data["expenseItems"]
    items = statements_data["items"]

    lines.append([total, total_income, total_expense, len(income_items), len(expense_items)])

    headers = ['Total', 'Income', 'Expense', '#IncomeCategories', '#ExpenseCategories']
    text += tabulate(lines, headers)

    text += "\n\n"

    headers = ['Category', 'Income', 'Expense', 'Total']
    lines = [
        list(x.values())
        for x in items
    ]
    text += tabulate(lines, headers, numalign='right')

    click.echo(text.strip())


def _timestamp_ms_to_date(epoch_ms) -> datetime or None:
    """Convert millisecond timestamp to datetime."""
    if epoch_ms:
        return datetime.fromtimestamp(epoch_ms / 1000, timezone.utc)


if __name__ == '__main__':
    cli()
