from game.board import Board
from game.rules import can_connect


class CSP:

    def __init__(self, board: Board):
        self.board = board
        self.variables = board.find_all_pairs()

    def is_consistent(self, assigned_order, candidate_pair):

        sim_board = self.board.clone()
        for (r1, c1, r2, c2) in assigned_order:
            sim_board.remove(r1, c1, r2, c2)

        r1, c1, r2, c2 = candidate_pair
        return can_connect(sim_board, r1, c1, r2, c2)

    def is_complete(self, assigned_order):
        return len(assigned_order) == len(self.variables)
