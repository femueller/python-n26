from n26.api import GET

from tests.test_api_base import N26TestBase, mock_requests, mock_config


class StandingOrdersTests(N26TestBase):
    """Standing orders tests"""

    @mock_config()
    @mock_requests(method=GET, response_file="standing_orders.json")
    def test_standing_orders_cli(self):
        from n26.cli import standing_orders
        result = self._run_cli_cmd(standing_orders)
        self.assertIsNotNone(result.output)
        self.assertIn('Mr. Anderson', result.output)
        self.assertIn('INWX', result.output)
        self.assertIn('30', result.output)
        self.assertIn('WEEKLY', result.output)
        self.assertIn('MONTHLY', result.output)
        self.assertIn('YEARLY', result.output)
        self.assertIn('2019-04-01 00:29:49.461000+00:00', result.output)
