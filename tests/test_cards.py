from n26.api import GET, POST
from tests.test_api_base import N26TestBase, mock_requests


class CardsTests(N26TestBase):
    """Cards tests"""

    @mock_requests(method=GET, response_file="cards.json")
    def test_get_cards(self):
        result = self._underTest.get_cards()
        self.assertIsNotNone(result)

    @mock_requests(method=GET, response_file="cards.json")
    @mock_requests(method=POST, response_file="card_block_single.json")
    def test_block_card_cli_single(self):
        from n26.cli import card_block
        card_id = "12345678-1234-abcd-abcd-1234567890ab"
        result = self._run_cli_cmd(card_block, ["--card", card_id])
        self.assertEqual(result.output, "Blocked card: {}\n".format(card_id))

    @mock_requests(method=GET, response_file="cards.json")
    @mock_requests(method=POST, response_file="card_block_single.json")
    def test_block_card_cli_all(self):
        from n26.cli import card_block
        card_id_1 = "12345678-1234-abcd-abcd-1234567890ab"
        card_id_2 = "22345678-1234-abcd-abcd-1234567890ab"

        result = self._run_cli_cmd(card_block)
        self.assertEqual(result.output, "Blocked card: {}\nBlocked card: {}\n".format(card_id_1, card_id_2))

    @mock_requests(method=GET, response_file="cards.json")
    @mock_requests(method=POST, response_file="card_unblock_single.json")
    def test_unblock_card_cli_single(self):
        from n26.cli import card_unblock
        card_id = "12345678-1234-abcd-abcd-1234567890ab"
        result = self._run_cli_cmd(card_unblock, ["--card", card_id])
        self.assertEqual(result.output, "Unblocked card: {}\n".format(card_id))

    @mock_requests(method=GET, response_file="cards.json")
    @mock_requests(method=POST, response_file="card_unblock_single.json")
    def test_unblock_card_cli_all(self):
        from n26.cli import card_unblock
        card_id_1 = "12345678-1234-abcd-abcd-1234567890ab"
        card_id_2 = "22345678-1234-abcd-abcd-1234567890ab"

        result = self._run_cli_cmd(card_unblock)
        self.assertEqual(result.output, "Unblocked card: {}\nUnblocked card: {}\n".format(card_id_1, card_id_2))
