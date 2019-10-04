import functools
import logging
import webbrowser
from datetime import datetime, timezone
from typing import Tuple

import click
from requests import HTTPError
from tabulate import tabulate

import n26.api as api
from n26.const import AMOUNT, CURRENCY, REFERENCE_TEXT, ATM_WITHDRAW, CARD_STATUS_ACTIVE, DATETIME_FORMATS

LOGGER = logging.getLogger(__name__)

API_CLIENT = api.Api()

JSON_OUTPUT = False
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


def auth_decorator(func: callable):
    """
    Decorator ensuring authentication before making api requests
    :param func: function to patch
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        new_auth = False
        try:
            API_CLIENT.refresh_authentication()
        except HTTPError as http_error:
            if http_error.response.status_code != 401:
                raise http_error
            new_auth = True
        except AssertionError:
            new_auth = True

        if new_auth:
            hint = click.style("Initiating authentication flow, please check your phone to approve login.", fg="yellow")
            click.echo(hint)

            API_CLIENT.authenticate()

            success = click.style("Authentication successful :)", fg="green")
            click.echo(success)

        return func(*args, **kwargs)

    return wrapper


# Cli returns command line requests
@click.group(context_settings=CONTEXT_SETTINGS)
@click.option("-json", default=False, type=bool, is_flag=True)
@click.version_option()
def cli(json: bool):
    """Interact with the https://n26.com API via the command line."""
    global JSON_OUTPUT
    JSON_OUTPUT = json


@cli.command()
@auth_decorator
def addresses():
    """ Show account addresses """
    addresses_data = API_CLIENT.get_addresses().get('data')
    if JSON_OUTPUT:
        _print_json(addresses_data)
        return

    headers = ['Type', 'Country', 'City', 'Zip code', 'Street', 'Number',
               'Address line 1', 'Address line 2',
               'Created', 'Updated']
    keys = ['type', 'countryName', 'cityName', 'zipCode', 'streetName', 'houseNumberBlock',
            'addressLine1', 'addressLine2',
            _datetime_extractor('created'), _datetime_extractor('updated')]
    table = _create_table_from_dict(headers, keys, addresses_data, numalign='right')
    click.echo(table)


@cli.command()
@auth_decorator
def info():
    """ Get account information """
    account_info = API_CLIENT.get_account_info()
    if JSON_OUTPUT:
        _print_json(account_info)
        return

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
@auth_decorator
def status():
    """ Get account statuses """
    account_statuses = API_CLIENT.get_account_statuses()
    if JSON_OUTPUT:
        _print_json(account_statuses)
        return

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
@auth_decorator
def balance():
    """ Show account balance """
    balance_data = API_CLIENT.get_balance()
    if JSON_OUTPUT:
        _print_json(balance_data)
        return

    amount = balance_data.get('availableBalance')
    currency = balance_data.get('currency')
    click.echo("{} {}".format(amount, currency))


@cli.command()
def browse():
    """ Browse on the web https://app.n26.com/ """
    webbrowser.open('https://app.n26.com/')


@cli.command()
@auth_decorator
def spaces():
    """ Show spaces """
    spaces_data = API_CLIENT.get_spaces()["spaces"]
    if JSON_OUTPUT:
        _print_json(spaces_data)
        return

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
@auth_decorator
def cards():
    """ Shows a list of cards """
    cards_data = API_CLIENT.get_cards()
    if JSON_OUTPUT:
        _print_json(cards_data)
        return

    headers = ['Id', 'Masked Pan', 'Type', 'Design', 'Status', 'Activated', 'Pin defined', 'Expires']
    keys = [
        'id',
        'maskedPan',
        'cardType',
        'design',
        lambda x: "active" if (x.get('status') == CARD_STATUS_ACTIVE) else x.get('status'),
        _datetime_extractor('cardActivated'),
        _datetime_extractor('pinDefined'),
        _datetime_extractor('expirationDate', date_only=True),
    ]
    text = _create_table_from_dict(headers=headers, value_functions=keys, data=cards_data, numalign='right')

    click.echo(text.strip())


@cli.command()
@click.option('--card', default=None, type=str, help='ID of the card to block. Omitting this will block all cards.')
@auth_decorator
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
@auth_decorator
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
@auth_decorator
def limits():
    """ Show n26 account limits """
    _limits()


@cli.command()
@click.option('--withdrawal', default=None, type=int, help='Daily withdrawal limit.')
@click.option('--payment', default=None, type=int, help='Daily payment limit.')
@auth_decorator
def set_limits(withdrawal: int, payment: int):
    """ Set n26 account limits """
    API_CLIENT.set_account_limits(withdrawal, payment)
    _limits()


def _limits():
    limits_data = API_CLIENT.get_account_limits()

    if JSON_OUTPUT:
        _print_json(limits_data)
        return

    headers = ['Name', 'Amount', 'Country List']
    keys = ['limit', 'amount', 'countryList']
    text = _create_table_from_dict(headers=headers, value_functions=keys, data=limits_data, numalign='right')

    click.echo(text)


@cli.command()
@auth_decorator
def contacts():
    """ Show your n26 contacts """
    contacts_data = API_CLIENT.get_contacts()

    if JSON_OUTPUT:
        _print_json(contacts_data)
        return

    headers = ['Id', 'Name', 'IBAN']
    keys = ['id', 'name', 'subtitle']
    text = _create_table_from_dict(headers=headers, value_functions=keys, data=contacts_data, numalign='right')

    click.echo(text.strip())


@cli.command()
@auth_decorator
def statements():
    """ Show your n26 statements  """
    statements_data = API_CLIENT.get_statements()

    if JSON_OUTPUT:
        _print_json(statements_data)
        return

    headers = ['Id', 'Url', 'Visible TS', 'Month', 'Year']
    keys = ['id', 'url', 'visibleTS', 'month', 'year']
    text = _create_table_from_dict(headers=headers, value_functions=keys, data=statements_data, numalign='right')

    click.echo(text.strip())


@cli.command()
@click.option('--categories', default=None, type=str,
              help='Comma separated list of category IDs.')
@click.option('--pending', default=None, type=bool,
              help='Whether to show only pending transactions.')
@click.option('--from', 'param_from', default=None, type=click.DateTime(DATETIME_FORMATS),
              help='Start time limit for statistics.')
@click.option('--to', 'param_to', default=None, type=click.DateTime(DATETIME_FORMATS),
              help='End time limit for statistics.')
@click.option('--text-filter', default=None, type=str, help='Text filter.')
@click.option('--limit', default=None, type=click.IntRange(1, 10000), help='Limit transaction output.')
@auth_decorator
def transactions(categories: str, pending: bool, param_from: datetime or None, param_to: datetime or None,
                 text_filter: str, limit: int):
    """ Show transactions (default: 5) """
    if not JSON_OUTPUT and not pending and not param_from and not limit:
        limit = 5
        click.echo(click.style("Output is limited to {} entries.".format(limit), fg="yellow"))

    from_timestamp, to_timestamp = _parse_from_to_timestamps(param_from, param_to)
    transactions_data = API_CLIENT.get_transactions(from_time=from_timestamp, to_time=to_timestamp,
                                                    limit=limit, pending=pending, text_filter=text_filter,
                                                    categories=categories)

    if JSON_OUTPUT:
        _print_json(transactions_data)
        return

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
            _datetime_extractor('visibleTS')(transaction),
            "{} {}".format(amount, currency),
            "{}\n{}".format(sender_name, sender_iban),
            "{}\n{}".format(recipient_name, recipient_iban),
            _insert_newlines(message),
            recurring
        ])

    headers = ['Date', 'Amount', 'From', 'To', 'Message', 'Recurring']
    text = tabulate(lines, headers, numalign='right')

    click.echo(text.strip())


@cli.command("standing-orders")
@auth_decorator
def standing_orders():
    """Show your standing orders"""
    standing_orders_data = API_CLIENT.get_standing_orders()

    if JSON_OUTPUT:
        _print_json(standing_orders_data)
        return

    headers = ['To',
               'Amount',
               'Frequency',
               'Until',
               'Every',
               'First execution', 'Next execution',
               'Executions',
               'Created', 'Updated']
    values = ['partnerName',
              lambda x: "{} {}".format(x.get('amount'), x.get('currencyCode').get('currencyCode')),
              'executionFrequency',
              _datetime_extractor('stopTS', date_only=True),
              _day_of_month_extractor('initialDayOfMonth'),
              _datetime_extractor('firstExecutingTS', date_only=True),
              _datetime_extractor('nextExecutingTS', date_only=True),
              'executionCounter',
              _datetime_extractor('created'),
              _datetime_extractor('updated')]
    text = _create_table_from_dict(headers, value_functions=values, data=standing_orders_data['data'])

    click.echo(text.strip())


@cli.command()
@click.option('--from', 'param_from', default=None, type=click.DateTime(DATETIME_FORMATS),
              help='Start time limit for statistics.')
@click.option('--to', 'param_to', default=None, type=click.DateTime(DATETIME_FORMATS),
              help='End time limit for statistics.')
@auth_decorator
def statistics(param_from: datetime or None, param_to: datetime or None):
    """Show your n26 statistics"""

    from_timestamp, to_timestamp = _parse_from_to_timestamps(param_from, param_to)
    statements_data = API_CLIENT.get_statistics(from_time=from_timestamp, to_time=to_timestamp)

    if JSON_OUTPUT:
        _print_json(statements_data)
        return

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


def _print_json(data: dict or list):
    """
    Pretty-Prints the given object to the  console
    :param data: data to print
    """
    import json
    json_data = json.dumps(data, indent=2)
    click.echo(json_data)


def _parse_from_to_timestamps(param_from: datetime or None, param_to: datetime or None) -> Tuple[int, int]:
    """
    Parses cli datetime inputs for "from" and "to" parameters
    :param param_from: "from" input
    :param param_to: "to" input
    :return: timestamps ready to be used by the api
    """
    from_timestamp = None
    to_timestamp = None
    if param_from is not None:
        from_timestamp = int(param_from.timestamp() * 1000)
        if param_to is None:
            # if --from is set, --to must also be set
            param_to = datetime.utcnow()
    if param_to is not None:
        if param_from is None:
            # if --to is set, --from must also be set
            from_timestamp = 1
        to_timestamp = int(param_to.timestamp() * 1000)

    return from_timestamp, to_timestamp


def _timestamp_ms_to_date(epoch_ms: int) -> datetime or None:
    """
    Convert millisecond timestamp to UTC datetime.

    :param epoch_ms: milliseconds since 1970 in CET
    :return: a UTC datetime object
    """
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


def _datetime_extractor(key: str, date_only: bool = False):
    """
    Helper function to extract a datetime value from a dict
    :param key: the dictionary key used to access the value
    :param date_only: removes the time from the output
    :return: an extractor function
    """

    if date_only:
        fmt = "%x"
    else:
        fmt = "%x %X"

    def extractor(dictionary: dict):
        value = dictionary.get(key)
        time = _timestamp_ms_to_date(value)
        if time is None:
            return None
        else:
            time = time.astimezone()
            return time.strftime(fmt)

    return extractor


def _day_of_month_extractor(key: str):
    def extractor(dictionary: dict):
        value = dictionary.get(key)
        if value is None:
            return None
        else:
            import inflect
            engine = inflect.engine()
            return engine.ordinal(value)

    return extractor


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
