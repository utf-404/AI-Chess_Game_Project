import unittest
from unittest.mock import Mock, patch

import chess
import server


class ServerMoveTests(unittest.TestCase):
    def test_player_move_receives_ai_reply(self):
        connection = Mock()
        connection.recv.side_effect = [b'e2e4', b'']
        with patch.object(server, 'game', chess.Game()), patch.object(
            server, 'get_AI_move',
            side_effect=lambda game: chess.parse_move_code(game, 'e7e5'),
        ):
            server.handle_client(connection, ('127.0.0.1', 12345))
            connection.sendall.assert_called_once_with(b'e7e5')
            self.assertEqual(server.game.to_move, chess.WHITE)
        connection.close.assert_called_once()


if __name__ == '__main__':
    unittest.main()
