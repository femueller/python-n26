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

DAILY_WITHDRAWAL_LIMIT = 'ATM_DAILY_ACCOUNT'
DAILY_PAYMENT_LIMIT = 'POS_DAILY_ACCOUNT'
