import webbrowser
from datetime import datetime, timezone

import click
from tabulate import tabulate

import n26.api as api
from n26.const import AMOUNT, CURRENCY, REFERENCE_TEXT, ATM_WITHDRAW

API_CLIENT = api.Api()

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


# Cli returns command line requests
@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    """Interact with the https://n26.com API via the command line."""


client = api.Api()


@cli.command()
def addresses():
    """ Show account addresses """
    addresses_data = API_CLIENT.get_addresses().get('data')

    headers = ['Type', 'Country', 'City', 'Zip code', 'Street', 'Number',
               'Address line 1', 'Address line 2',
               'Created', 'Updated']
    keys = ['type', 'countryName', 'cityName', 'zipCode', 'streetName', 'houseNumberBlock',
            'addressLine1', 'addressLine2',
            _datetime_extractor('created'), _datetime_extractor('updated')]
    table = _create_table_from_dict(headers, keys, addresses_data, numalign='right')
    click.echo(table)


@cli.command()
def info():
    """ Get account information """
    account_info = API_CLIENT.get_account_info()

    lines = [
        ["Name:", "{} {}".format(account_info.get('firstName'), account_info.get('lastName'))],
        ["Email:", account_info.get('email')],
        ["Gender:", account_info.get('gender')],
        ["Nationality:", account_info.get('nationality')],
        ["Phone:", account_info.get('mobilePhoneNumber')]
    ]

    text = tabulate(lines, [], tablefmt="plain", colalign=["right", "left"])

    click.echo(text)


@cli.command()
def status():
    """ Get account statuses """
    account_statuses = API_CLIENT.get_account_statuses()

    lines = [
        ["Account created:", _timestamp_ms_to_date(account_statuses.get('created'))],
        ["Account updated:", _timestamp_ms_to_date(account_statuses.get('updated'))],
        ["Account closed:", account_statuses.get('accountClosed')],
        ["Card activation completed:", _timestamp_ms_to_date(account_statuses.get('cardActivationCompleted'))],
        ["Card issued:", _timestamp_ms_to_date(account_statuses.get('cardIssued'))],
        ["Core data updated:", _timestamp_ms_to_date(account_statuses.get('coreDataUpdated'))],
        ["Email validation initiated:", _timestamp_ms_to_date(account_statuses.get('emailValidationInitiated'))],
        ["Email validation completed:", _timestamp_ms_to_date(account_statuses.get('emailValidationCompleted'))],
        ["First incoming transaction:", _timestamp_ms_to_date(account_statuses.get('firstIncomingTransaction'))],
        ["Flex account:", account_statuses.get('flexAccount')],
        ["Flex account confirmed:", _timestamp_ms_to_date(account_statuses.get('flexAccountConfirmed'))],
        ["Is deceased:", account_statuses.get('isDeceased')],
        ["Pairing State:", account_statuses.get('pairingState')],
        ["Phone pairing initiated:", _timestamp_ms_to_date(account_statuses.get('phonePairingInitiated'))],
        ["Phone pairing completed:", _timestamp_ms_to_date(account_statuses.get('phonePairingCompleted'))],
        ["Pin definition completed:", _timestamp_ms_to_date(account_statuses.get('pinDefinitionCompleted'))],
        ["Product selection completed:", _timestamp_ms_to_date(account_statuses.get('productSelectionCompleted'))],
        ["Signup step:", account_statuses.get('signupStep')],
        ["Single step signup:", _timestamp_ms_to_date(account_statuses.get('singleStepSignup'))],
        ["Unpairing process status:", account_statuses.get('unpairingProcessStatus')],
    ]

    text = tabulate(lines, [], tablefmt="plain", colalign=["right", "left"])

    click.echo(text)


@cli.command()
def balance():
    """ Show account balance """
    balance_data = API_CLIENT.get_balance()
    amount = balance_data.get('availableBalance')
    currency = balance_data.get('currency')
    click.echo("{} {}".format(amount, currency))


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
        line.append("{} {}".format(available_balance, currency))

        if 'goal' in space:
            goal = space['goal']['amount']
            percentage = available_balance / goal

            line.append("{} {}".format(goal, currency))
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
def card_block(card: str):
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
def card_unblock(card: str):
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

    headers = ['Name', 'Amount', 'Country List']
    keys = ['limit', 'amount', 'countryList']
    text = _create_table_from_dict(headers=headers, value_functions=keys, data=limits_data, numalign='right')

    click.echo(text)


@cli.command()
def contacts():
    """ Show your n26 contacts  """
    contacts_data = API_CLIENT.get_contacts()

    headers = ['Id', 'Name', 'Subtitle']
    keys = ['id', 'name', 'subtitle']
    text = _create_table_from_dict(headers=headers, value_functions=keys, data=contacts_data, numalign='right')

    click.echo(text.strip())


@cli.command()
def statements():
    """ Show your n26 statements  """
    statements_data = API_CLIENT.get_statements()

    headers = ['Id', 'Url', 'Visible TS', 'Month', 'Year']
    keys = ['id', 'url', 'visibleTS', 'month', 'year']
    text = _create_table_from_dict(headers=headers, value_functions=keys, data=statements_data, numalign='right')

    click.echo(text.strip())


@cli.command()
@click.option('--categories', default=None, type=str,
              help='Comma separated list of category IDs.')
@click.option('--pending', default=None, type=bool,
              help='Whether to show only pending transactions.')
@click.option('--from', 'param_from', default=None, type=int,
              help='Start time limit for statistics. Timestamp - milliseconds since 1970 in CET')
@click.option('--to', default=None, type=int,
              help='End time limit for statistics. Timestamp - milliseconds since 1970 in CET')
@click.option('--text-filter', default=None, type=str, help='Text filter.')
@click.option('--limit', default=None, type=click.IntRange(1, 10000), help='Limit transaction output.')
def transactions(categories: str, pending: bool, param_from: int, to: int, text_filter: str, limit: int):
    """ Show transactions (default: 5) """
    if not pending and not limit:
        limit = 5
        click.echo(click.style("Output is limited to {} entries.".format(limit), fg="yellow"))

    transactions_data = API_CLIENT.get_transactions(from_time=param_from, to_time=to, limit=limit, pending=pending,
                                                    text_filter=text_filter, categories=categories)

    lines = []
    for i, transaction in enumerate(transactions_data):
        amount = transaction.get(AMOUNT, 0)
        currency = transaction.get(CURRENCY, None)

        if amount < 0:
            sender_name = "You"
            sender_iban = ""
            recipient_name = transaction.get('merchantName', transaction.get('partnerName', ''))
            recipient_iban = transaction.get('partnerIban', '')
        else:
            sender_name = transaction.get('partnerName', '')
            sender_iban = transaction.get('partnerIban', '')
            recipient_name = "You"
            recipient_iban = ""

        recurring = transaction.get('recurring', '')

        if transaction['type'] == ATM_WITHDRAW:
            message = "ATM Withdrawal"
        else:
            message = transaction.get(REFERENCE_TEXT)

        lines.append([
            "{} {}".format(amount, currency),
            "{}\n{}".format(sender_name, sender_iban),
            "{}\n{}".format(recipient_name, recipient_iban),
            _insert_newlines(message),
            recurring
        ])

    headers = ['Amount', 'From', 'To', 'Message', 'Recurring']
    text = tabulate(lines, headers, numalign='right')

    click.echo(text.strip())


@cli.command("standing-orders")
def standing_orders():
    """Show your standing orders"""
    standing_orders_data = API_CLIENT.get_standing_orders()

    headers = ['To',
               'Amount',
               'Frequency',
               'Until',
               'Initial day of month',
               'First execution', 'Next execution',
               'Executions',
               'Created', 'Updated']
    values = ['partnerName',
              lambda x: "{} {}".format(x.get('amount'), x.get('currencyCode').get('currencyCode')),
              'executionFrequency',
              _datetime_extractor('stopTS'),
              'initialDayOfMonth',
              _datetime_extractor('firstExecutingTS'),
              _datetime_extractor('nextExecutingTS'),
              'executionCounter',
              _datetime_extractor('created'),
              _datetime_extractor('updated')]
    text = _create_table_from_dict(headers, value_functions=values, data=standing_orders_data['data'])

    click.echo(text.strip())


@cli.command()
@click.option('--from', 'param_from', default=None, type=int,
              help='Start time limit for statistics. Timestamp - milliseconds since 1970 in CET')
@click.option('--to', default=None, type=int,
              help='End time limit for statistics. Timestamp - milliseconds since 1970 in CET')
def statistics(param_from: int, to: int):
    """Show your n26 statistics"""
    statements_data = API_CLIENT.get_statistics(from_time=param_from, to_time=to)

    text = "From: %s\n" % (_timestamp_ms_to_date(statements_data["from"]))
    text += "To:   %s\n\n" % (_timestamp_ms_to_date(statements_data["to"]))

    headers = ['Total', 'Income', 'Expense', '#IncomeCategories', '#ExpenseCategories']
    values = ['total', 'totalIncome', 'totalExpense',
              lambda x: len(x.get('incomeItems')),
              lambda x: len(x.get('expenseItems'))]

    text += _create_table_from_dict(headers, value_functions=values, data=[statements_data])

    text += "\n\n"

    headers = ['Category', 'Income', 'Expense', 'Total']
    keys = ['id', 'income', 'expense', 'total']
    text += _create_table_from_dict(headers, keys, statements_data["items"], numalign='right')

    click.echo(text.strip())


def _timestamp_ms_to_date(epoch_ms: int) -> datetime or None:
    """Convert millisecond timestamp to datetime."""
    if epoch_ms:
        return datetime.fromtimestamp(epoch_ms / 1000, timezone.utc)


def _create_table_from_dict(headers: list, value_functions: list, data: list, **tabulate_args) -> str:
    """
    Helper function to turn a list of dictionaries into a table.

    Note: This method does NOT work with nested dictionaries and will only inspect top-level keys

    :param headers: the headers to use for the columns
    :param value_functions: function that extracts the value for a given key. Can also be a simple string that
                            will be used as dictionary key.
    :param data: a list of dictionaries containing the data
    :return: a table
    """

    if len(headers) != len(value_functions):
        raise AttributeError("Number of headers does not match number of keys!")

    lines = []
    if isinstance(data, list):
        for dictionary in data:
            line = []
            for value_function in value_functions:
                if callable(value_function):
                    value = value_function(dictionary)
                    line.append(value)
                else:
                    # try to use is as a dict key
                    line.append(dictionary.get(str(value_function)))

            lines.append(line)

    return tabulate(tabular_data=lines, headers=headers, **tabulate_args)


def _datetime_extractor(key: str):
    """
    Helper function to extract a datetime value from a dict
    :param key: the dictionary key used to access the value
    :return: an extractor function
    """
    return lambda x: _timestamp_ms_to_date(x.get(key))


def _insert_newlines(text: str, n=40):
    """
    Inserts a newline into the given text every n characters.
    :param text: the text to break
    :param n:
    :return:
    """
    if not text:
        return ""

    lines = []
    for i in range(0, len(text), n):
        lines.append(text[i:i + n])
    return '\n'.join(lines)


if __name__ == '__main__':
    cli()
