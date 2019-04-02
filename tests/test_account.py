from n26.api import GET
from tests.test_api_base import N26TestBase, mock_requests


class AccountTests(N26TestBase):
    """Account tests"""

    @mock_requests(method=GET, response_file="account_info.json")
    def test_get_account_info(self):
        result = self._underTest.get_account_info()
        self.assertEqual(result["email"], "john.doe@example.com")

    @mock_requests(method=GET, response_file="account_info.json")
    def test_get_account_info_cli(self):
        from n26.cli import info
        result = self._run_cli_cmd(info)
        self.assertIsNotNone(result.output)

    @mock_requests(method=GET, response_file="account_statuses.json")
    def test_get_account_statuses(self):
        result = self._underTest.get_account_statuses()
        self.assertIsNotNone(result)

    @mock_requests(method=GET, response_file="account_limits.json")
    def test_get_account_limits(self):
        result = self._underTest.get_account_limits()
        self.assertIsNotNone(result)

    @mock_requests(method=GET, response_file="account_limits.json")
    def test_limits_cli(self):
        from n26.cli import limits
        result = self._run_cli_cmd(limits)
        self.assertIn("POS_DAILY_ACCOUNT", result.output)
        self.assertIn("ATM_DAILY_ACCOUNT", result.output)
        self.assertIn("2500", result.output)

    @mock_requests(method=GET, response_file="addresses.json")
    def test_get_addresses(self):
        result = self._underTest.get_addresses()
        self.assertIsNotNone(result)

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
