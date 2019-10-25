from n26.api import GET

from tests.test_api_base import N26TestBase, mock_requests


class TransactionsTests(N26TestBase):
    """Transactions tests"""

    @mock_requests(method=GET, response_file="transactions.json")
    def test_transactions_cli(self):
        from n26.cli import transactions
        result = self._run_cli_cmd(transactions, ["--from", "01/30/2019", "--to", "30.01.2020"])
        self.assertIsNotNone(result.output)
