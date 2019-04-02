from n26.api import GET
from tests.test_api_base import N26TestBase, mock_requests


class CardsTests(N26TestBase):
    """Cards tests"""

    @mock_requests(method=GET, response_file="cards.json")
    def test_get_cards(self):
        result = self._underTest.get_cards()
        self.assertIsNotNone(result)
