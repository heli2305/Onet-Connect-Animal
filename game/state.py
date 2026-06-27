from game.board import Board
from game.rules import can_connect


class GameState:

    def __init__(self, board: Board):
        self.board = board

    def is_goal(self) -> bool:
        return self.board.is_solved()

    def get_actions(self):
        actions = []
        for (r1, c1, r2, c2) in self.board.find_all_pairs():
            if can_connect(self.board, r1, c1, r2, c2):
                actions.append((r1, c1, r2, c2))
        return actions

    def apply_action(self, action):
        r1, c1, r2, c2 = action
        new_board = self.board.clone()
        new_board.remove(r1, c1, r2, c2)
        return GameState(new_board)

    def heuristic(self) -> int:
        return self.board.num_remaining_tiles() // 2

    def key(self):
        return self.board.to_key()

    def __eq__(self, other):
        return isinstance(other, GameState) and self.key() == other.key()

    def __hash__(self):
        return hash(self.key())

    def __repr__(self):
        return f"GameState(remaining={self.board.num_remaining_tiles()})"


def make_initial_state(rows=6, cols=6, seed=None) -> GameState:
    board = Board(rows=rows, cols=cols, seed=seed)
    return GameState(board)
