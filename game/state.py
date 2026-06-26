"""
============================================================
BÀI TOÁN: "Giải toàn bộ bàn cờ nối thú"
============================================================
- State        : trạng thái bàn cờ hiện tại (board NxM, các ô đã xóa = 0)
- Action       : chọn 1 cặp ô (r1,c1,r2,c2) cùng loại thú, có đường nối
                 hợp lệ (theo rules.can_connect), để xóa khỏi bàn
- Result       : bàn cờ sau khi xóa cặp đó
- Goal-test    : bàn cờ trống hoàn toàn (board.is_solved())
- Step-cost    : 1 cho mỗi action (mỗi lần xóa 1 cặp = 1 bước)
- Heuristic h(state) = (số ô còn lại) / 2 = số cặp còn lại cần xóa.
  h là ADMISSIBLE (không bao giờ đánh giá quá cao) vì trong điều kiện
  tốt nhất (không bị kẹt), số bước còn lại tối thiểu đúng bằng đúng
  số cặp còn lại trên bàn.
"""

from game.board import Board
from game.rules import can_connect


class GameState:
    """
    Bọc 1 đối tượng Board thành 1 'state' đúng nghĩa cho bài toán search:
    bất biến khi đã tạo ra (immutable-style) và so sánh/hash được để
    cho vào các tập visited/explored.
    """

    def __init__(self, board: Board):
        self.board = board

    # ---------- Các hàm BẮT BUỘC của 1 bài toán search ----------

    def is_goal(self) -> bool:
        return self.board.is_solved()

    def get_actions(self):
        """
        Trả về list các action hợp lệ tại state này.
        Mỗi action là tuple (r1, c1, r2, c2).
        """
        actions = []
        for (r1, c1, r2, c2) in self.board.find_all_pairs():
            if can_connect(self.board, r1, c1, r2, c2):
                actions.append((r1, c1, r2, c2))
        return actions

    def apply_action(self, action):
        """Trả về 1 GameState MỚI sau khi áp dụng action (không sửa state cũ)."""
        r1, c1, r2, c2 = action
        new_board = self.board.clone()
        new_board.remove(r1, c1, r2, c2)
        return GameState(new_board)

    def heuristic(self) -> int:
        """h(state) = số cặp thú còn lại trên bàn (xem giải thích ở đầu file)."""
        return self.board.num_remaining_tiles() // 2

    # ---------- Các hàm tiện ích để dùng làm key trong visited-set ----------

    def key(self):
        return self.board.to_key()

    def __eq__(self, other):
        return isinstance(other, GameState) and self.key() == other.key()

    def __hash__(self):
        return hash(self.key())

    def __repr__(self):
        return f"GameState(remaining={self.board.num_remaining_tiles()})"


def make_initial_state(rows=6, cols=6, seed=None) -> GameState:
    """Hàm tiện ích: tạo 1 bàn cờ mới và bọc thành GameState ban đầu."""
    board = Board(rows=rows, cols=cols, seed=seed)
    return GameState(board)
