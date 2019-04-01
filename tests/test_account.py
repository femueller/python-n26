from n26.api import GET
from tests.test_api_base import N26TestBase, mock_api


class AccountTests(N26TestBase):
    """Account tests"""

    @mock_api(method=GET, response_file="account_info.json")
    def test_get_account_info(self):
        result = self._underTest.get_account_info()
        self.assertEqual(result["email"], "john.doe@example.com")

    @mock_api(method=GET, response_file="account_statuses.json")
    def test_get_account_statuses(self):
        result = self._underTest.get_account_statuses()
        self.assertIsNotNone(result)
