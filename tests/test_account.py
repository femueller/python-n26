from n26.api import GET, POST
from tests.test_api_base import N26TestBase, mock_requests


class AccountTests(N26TestBase):
    """Account tests"""

    @mock_requests(method=GET, response_file="account_info.json")
    def test_get_account_info_cli(self):
        from n26.cli import info
        result = self._run_cli_cmd(info)
        self.assertIsNotNone(result.output)

    @mock_requests(method=GET, response_file="account_statuses.json")
    def test_get_account_statuses_cli(self):
        from n26.cli import status
        result = self._run_cli_cmd(status)
        self.assertIn("PAIRED", result.output)

    @mock_requests(method=GET, response_file="account_limits.json")
    def test_limits_cli(self):
        from n26.cli import limits
        result = self._run_cli_cmd(limits)
        self.assertIn("POS_DAILY_ACCOUNT", result.output)
        self.assertIn("ATM_DAILY_ACCOUNT", result.output)
        self.assertIn("2500", result.output)

    @mock_requests(method=POST, response_file=None)
    @mock_requests(method=GET, response_file="account_limits.json")
    def test_set_limits_cli(self):
        from n26.cli import set_limits
        result = self._run_cli_cmd(set_limits, ["--withdrawal", 2500, "--payment", 2500])
        self.assertIn("POS_DAILY_ACCOUNT", result.output)
        self.assertIn("ATM_DAILY_ACCOUNT", result.output)
        self.assertIn("2500", result.output)

    @mock_requests(method=GET, response_file="addresses.json")
    def test_addresses_cli(self):
        from n26.cli import addresses
        result = self._run_cli_cmd(addresses)
        self.assertIn("Einbahnstraße", result.output)
        self.assertIn("SHIPPING", result.output)
        self.assertIn("PASSPORT", result.output)
        self.assertIn("LEGAL", result.output)

    @mock_requests(method=GET, response_file="contacts.json")
    def test_get_contacts(self):
        result = self._underTest.get_contacts()
        self.assertIsNotNone(result)

    @mock_requests(method=GET, response_file="contacts.json")
    def test_contacts_cli(self):
        from n26.cli import contacts
        result = self._run_cli_cmd(contacts)
        self.assertIn("ADAC", result.output)
        self.assertIn("Cyberport", result.output)
        self.assertIn("DB", result.output)
        self.assertIn("ELV", result.output)
        self.assertIn("Mindfactory", result.output)
        self.assertIn("Seegel", result.output)

    @mock_requests(method=GET, response_file="statements.json")
    def test_get_statements_cli(self):
        from n26.cli import statements
        result = self._run_cli_cmd(statements)
        self.assertIn("2016-11", result.output)
        self.assertIn("2017-01", result.output)
        self.assertIn("2018-01", result.output)
        self.assertIn("2019-01", result.output)
        self.assertIn("/api/statements/statement-2019-04", result.output)
        self.assertIn("1554076800000", result.output)

    @mock_requests(method=GET, response_file="statements.json")
    def test_get_statements_by_id_cli(self):
        from n26.cli import statements
        result = self._run_cli_cmd(statements, ["--id", "statement-2017-01"])
        self.assertEqual(len(result.output.split("\n")), 4)
        self.assertNotIn("2016-11", result.output)
        self.assertIn("/api/statements/statement-2017-01", result.output)
        self.assertNotIn("2018-01", result.output)
        self.assertNotIn("2019-01", result.output)
        self.assertNotIn("1554076800000", result.output)

    @mock_requests(method=GET, response_file="statements.json")
    def test_get_statements_by_date_cli(self):
        from n26.cli import statements
        result = self._run_cli_cmd(statements, ["--from", "2017-01-01", "--to", "2017-04-01"])
        self.assertEqual(len(result.output.split("\n")), 7)
        self.assertNotIn("2016-11", result.output)
        self.assertIn("/api/statements/statement-2017-01", result.output)
        self.assertIn("2017-02", result.output)
        self.assertIn("2017-03", result.output)
        self.assertIn("2017-04", result.output)
        self.assertNotIn("2018-01", result.output)
        self.assertNotIn("2019-01", result.output)
        self.assertNotIn("1554076800000", result.output)
