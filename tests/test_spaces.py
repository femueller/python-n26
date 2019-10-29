from n26.api import GET
from tests.test_api_base import N26TestBase, mock_requests


class SpacesTests(N26TestBase):
    """Spaces tests"""

    @mock_requests(method=GET, response_file="spaces.json")
    def test_spaces_cli(self):
        from n26.cli import spaces
        result = self._run_cli_cmd(spaces)
        self.assertRegex(result.output, r"\d*\.\d* \w*.*")
