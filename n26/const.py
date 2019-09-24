"""
transaction types and their meaning
"""
DEBIT_PAYMENT = "AA"
SEPA_WITHDRAW = "DD"
INCOMING_TRANSFER = "CT"
ATM_WITHDRAW = "PT"

"""
transaction item keys
"""
CURRENCY = 'currencyCode'
AMOUNT = 'amount'
REFERENCE_TEXT = 'referenceText'

CARD_STATUS_ACTIVE = 'M_ACTIVE'

DAILY_WITHDRAWAL_LIMIT = 'ATM_DAILY_ACCOUNT'
DAILY_PAYMENT_LIMIT = 'POS_DAILY_ACCOUNT'

DATETIME_FORMATS = [
    '%m/%d/%Y %H:%M:%S',
    '%m/%d/%Y',
    '%Y-%m-%d',
    '%Y-%m-%dT%H:%M:%S',
    '%Y-%m-%d %H:%M:%S',
    '%d.%m.%Y',
    '%d.%m.%Y %H:%M:%S'
]
