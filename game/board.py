import numpy as np
import random


ANIMAL_NAMES = [
    "buffalo", "chicken", "cow", "dog", "duck", "elephant", "frog", "giraffe",
    "gorilla", "monkey", "narwhal", "owl", "parrot", "penguin", "pig", "rabbit",
    "whale", "zebra"
]


class Board:

    def __init__(self, rows=6, cols=6, seed=None):
        assert (rows * cols) % 2 == 0, "Số ô trên bàn phải là số chẵn"
        self.rows = rows
        self.cols = cols
        self._rng = random.Random(seed)
        self.board = np.zeros((rows, cols), dtype=int)
        self._generate()

    def _is_solvable(self) -> bool:
        sim = self.clone()
        from game.rules import can_connect
        while True:
            pairs = sim.find_all_pairs()
            found = False
            for (r1, c1, r2, c2) in pairs:
                if can_connect(sim, r1, c1, r2, c2):
                    sim.remove(r1, c1, r2, c2)
                    found = True
                    break
            if not found:
                break
        return sim.is_solved()

    def _generate(self):
        total = self.rows * self.cols
        num_pairs = total // 2

        assert num_pairs <= len(ANIMAL_NAMES), (
            f"Bàn cờ {self.rows}x{self.cols} có {num_pairs} cặp, vượt quá {len(ANIMAL_NAMES)} loại thú."
        )

        tiles = []
        for i in range(1, num_pairs + 1):
            tiles.extend([i, i])

        while True:
            self._rng.shuffle(tiles)
            idx = 0
            for r in range(self.rows):
                for c in range(self.cols):
                    self.board[r][c] = tiles[idx]
                    idx += 1
            if self._is_solvable():
                break

    @staticmethod
    def animal_name(type_id: int) -> str:
        if type_id == 0:
            return None
        return ANIMAL_NAMES[(type_id - 1) % len(ANIMAL_NAMES)]

    def get(self, r, c):
        return self.board[r][c]

    def is_empty(self, r, c):
        return self.board[r][c] == 0

    def remove(self, r1, c1, r2, c2):
        self.board[r1][c1] = 0
        self.board[r2][c2] = 0

    def is_solved(self):
        return bool(np.all(self.board == 0))

    def find_all_pairs(self):
        positions = {}
        for r in range(self.rows):
            for c in range(self.cols):
                v = self.board[r][c]
                if v != 0:
                    positions.setdefault(v, []).append((r, c))
        pairs = []
        for v, pos_list in positions.items():
            for i in range(len(pos_list)):
                for j in range(i + 1, len(pos_list)):
                    pairs.append((*pos_list[i], *pos_list[j]))
        return pairs

    def clone(self):
        new = Board.__new__(Board)
        new.rows = self.rows
        new.cols = self.cols
        new._rng = self._rng
        new.board = self.board.copy()
        return new

    def to_key(self):
        return self.board.tobytes()

    def num_remaining_tiles(self):
        return int(np.count_nonzero(self.board))

    def __str__(self):
        lines = []
        for r in range(self.rows):
            row_str = " ".join(f"{self.board[r][c]:>2}" for c in range(self.cols))
            lines.append(row_str)
        return "\n".join(lines)
