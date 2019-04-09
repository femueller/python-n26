from n26.api import GET
from tests.test_api_base import N26TestBase, mock_requests, mock_config


class BalanceTest(N26TestBase):
    """Balance tests"""

    @mock_config()
    @mock_requests(method=GET, response_file="balance.json")
    def test_balance_cli(self):
        from n26.cli import balance
        result = self._run_cli_cmd(balance)
        self.assertRegex(result.output, r"\d*\.\d* \w*.*")
