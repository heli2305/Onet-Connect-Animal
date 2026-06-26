"""
board.py
--------
Quản lý bàn cờ game nối thú (kiểu Pikachu).

board[r][c] = 0   -> ô trống (đã bị xóa hoặc chưa có thú)
board[r][c] > 0   -> loại thú số (1..N), số này được map sang
                     tên 1 loài vật cụ thể để vẽ icon (xem ANIMAL_NAMES).

Đây là phần code NỀN, dùng chung cho toàn bộ 12 thuật toán trong đồ án.
Cố tình giữ đơn giản (numpy 2D, không dùng cấu trúc dữ liệu phức tạp)
để dễ giải thích trong báo cáo / lúc bảo vệ.
"""

import numpy as np
import random

# 18 loại thú có icon sẵn trong game/assets/icons_png/
# Số thứ tự (1..18) sẽ được dùng làm "mã loại thú" trên board.
ANIMAL_NAMES = [
    "buffalo", "chicken", "cow", "dog", "duck", "elephant", "frog", "giraffe",
    "gorilla", "monkey", "narwhal", "owl", "parrot", "penguin", "pig", "rabbit",
    "whale", "zebra"
]


class Board:
    """Quản lý bàn cờ game nối thú."""

    def __init__(self, rows=6, cols=6, seed=None):
        """
        rows, cols: kích thước bàn cờ. rows*cols PHẢI là số chẵn.
        seed: cố định random để demo lại được đúng 1 bàn cờ (tái lập kết quả
              khi so sánh các thuật toán với nhau).
        """
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
        """Trả về tên loài thú (str) ứng với 1 mã số trên board. 0 -> None."""
        if type_id == 0:
            return None
        return ANIMAL_NAMES[(type_id - 1) % len(ANIMAL_NAMES)]

    def get(self, r, c):
        return self.board[r][c]

    def is_empty(self, r, c):
        return self.board[r][c] == 0

    def remove(self, r1, c1, r2, c2):
        """Xóa 1 cặp khỏi bàn (đặt về 0)."""
        self.board[r1][c1] = 0
        self.board[r2][c2] = 0

    def is_solved(self):
        return bool(np.all(self.board == 0))

    def find_all_pairs(self):
        """Trả về list tất cả cặp (r1,c1,r2,c2) cùng loại còn trên bàn."""
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
        """Trả về bản sao độc lập của board (dùng khi thử 1 nhánh tìm kiếm)."""
        new = Board.__new__(Board)
        new.rows = self.rows
        new.cols = self.cols
        new._rng = self._rng
        new.board = self.board.copy()
        return new

    def to_key(self):
        """
        Chuyển bàn cờ thành 1 giá trị bất biến (hashable) để cho vào
        visited-set / explored-set của các thuật toán search.
        """
        return self.board.tobytes()

    def num_remaining_tiles(self):
        return int(np.count_nonzero(self.board))

    def __str__(self):
        lines = []
        for r in range(self.rows):
            row_str = " ".join(f"{self.board[r][c]:>2}" for c in range(self.cols))
            lines.append(row_str)
        return "\n".join(lines)
