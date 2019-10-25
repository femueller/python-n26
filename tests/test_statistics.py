from n26.api import GET

from tests.test_api_base import N26TestBase, mock_requests


class StatisticsTests(N26TestBase):
    """Statistics tests"""

    @mock_requests(method=GET, response_file="statistics.json")
    def test_statistics_cli(self):
        from n26.cli import statistics
        result = self._run_cli_cmd(statistics)
        self.assertIsNotNone(result.output)
