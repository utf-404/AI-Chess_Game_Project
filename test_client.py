import importlib.util
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, MagicMock, patch

import chess


def load_module(name):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ClientTests(unittest.TestCase):
    def setUp(self):
        self.pygame = MagicMock()
        self.pygame.QUIT = 1
        self.pygame.MOUSEBUTTONDOWN = 2
        self.pygame.MOUSEBUTTONUP = 3
        self.pygame.event.get.return_value = [SimpleNamespace(type=1)]
        self.modules = patch.dict(sys.modules, {'pygame': self.pygame})
        self.modules.start()
        self.addCleanup(self.modules.stop)

    def test_import_gui_does_not_start_a_game(self):
        with patch('random.choice', side_effect=lambda items: items[0]):
            load_module('gui')
        self.pygame.event.get.assert_not_called()
        self.pygame.display.flip.assert_not_called()

    def test_drag_applies_player_and_ai_moves_and_quit_returns(self):
        gui = load_module('gui')
        with patch.dict(sys.modules, {'gui': gui}):
            client = load_module('client')
        self.pygame.event.get.side_effect = [
            [SimpleNamespace(type=3), SimpleNamespace(type=2), SimpleNamespace(type=3)],
            [SimpleNamespace(type=1)],
        ]
        self.pygame.mouse.get_pos.side_effect = [(0, 360), (0, 300)]
        client.send_move_to_server = Mock(return_value='a7a6')
        client.handle_gui()
        client.send_move_to_server.assert_called_once_with('a2a3')
        self.assertEqual(chess.get_piece(client.game.board, chess.str2bb('a3')), chess.WHITE | chess.PAWN)
        self.assertEqual(chess.get_piece(client.game.board, chess.str2bb('a6')), chess.BLACK | chess.PAWN)
        self.pygame.quit.assert_called_once()


if __name__ == '__main__':
    unittest.main()
