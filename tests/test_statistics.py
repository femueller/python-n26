from n26.api import GET

from tests.test_api_base import N26TestBase, mock_requests, mock_config


class StatisticsTests(N26TestBase):
    """Statistics tests"""

    @mock_requests(method=GET, response_file="statistics.json")
    def test_get_statistics(self):
        result = self._underTest.get_statistics()
        self.assertIsNotNone(result)

    @mock_config
    @mock_requests(method=GET, response_file="statistics.json")
    def test_statistics_cli(self):
        from n26.cli import statistics
        result = self._run_cli_cmd(statistics)
        self.assertIsNotNone(result.output)
