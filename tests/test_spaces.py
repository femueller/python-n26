from n26.api import GET
from tests.test_api_base import N26TestBase, mock_requests


class SpacesTests(N26TestBase):
    """Spaces tests"""

    @mock_requests(method=GET, response_file="spaces.json")
    def test_get_spaces(self):
        result = self._underTest.get_spaces()
        self.assertIsNotNone(result)
