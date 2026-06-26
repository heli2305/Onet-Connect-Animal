"""
csp_problem.py
--------------
Định nghĩa BÀI TOÁN CSP (Constraint Satisfaction Problem) cho nhóm
Backtracking / Forward Checking / AC-3 / Min-Conflicts.

CÁCH MAP BÀI TOÁN "GIẢI BÀN CỜ" THÀNH 1 CSP:
----------------------------------------------
- BIẾN (variables): mỗi cặp thú trên bàn là 1 biến X_1, X_2, ..., X_n
  (n = tổng số cặp).
- DOMAIN (miền giá trị) của mỗi biến X_i: domain ban đầu là
  {0, 1, ..., n-1} - nghĩa là "X_i sẽ được xóa ở LƯỢT THỨ MẤY"
  (1 số nguyên đại diện cho VỊ TRÍ trong thứ tự xóa).
- RÀNG BUỘC (constraints):
    1. Ràng buộc ALL-DIFFERENT: mọi biến phải được gán giá trị
       (lượt xóa) KHÁC NHAU (vì 2 cặp không thể xóa cùng 1 lượt).
    2. Ràng buộc ĐỘNG (phụ thuộc trạng thái): cặp X_i được gán lượt
       xóa thứ k CHỈ HỢP LỆ nếu, sau khi đã xóa hết các cặp được gán
       lượt 0..k-1, cặp X_i còn nối được (theo rules.can_connect).
       Đây là điểm ĐẶC BIỆT của bài toán này so với CSP "kinh điển"
       (N-Queens, Map Coloring...) - ràng buộc không cố định mà phụ
       thuộc vào THỨ TỰ các biến khác đã được gán trước đó. Cần nói
       rõ điều này trong báo cáo vì đây là điểm khác biệt thú vị.

Vì ràng buộc (2) phụ thuộc thứ tự, cách triển khai THỰC TẾ đơn giản
hơn là: backtracking sẽ gán lượt xóa theo thứ tự TĂNG DẦN (0, 1, 2,
...) - tức là tại mỗi bước của thuật toán, ta đang chọn "biến nào sẽ
được gán lượt xóa TIẾP THEO", và kiểm tra ràng buộc (2) chính là gọi
rules.can_connect tại bàn cờ hiện tại (đã xóa các cặp gán trước đó).
Cách làm này tương đương 1 CSP "biến thứ tự" (ordering CSP) - khá phổ
biến trong các bài toán lập kế hoạch (scheduling).
"""

from game.board import Board
from game.rules import can_connect


class PikachuCSP:
    """
    Đại diện cho 1 bài toán CSP: biến = các cặp thú, domain = vị trí
    lượt xóa (0..n-1), ràng buộc = ALL-DIFFERENT + "nối được tại thời
    điểm xóa".

    Để đơn giản hóa triển khai (đúng tinh thần "code dễ hiểu"), ta
    KHÔNG lưu domain dạng "vị trí" tường minh, mà coi bài toán là:
    "Tìm 1 THỨ TỰ (permutation) của các biến X_1..X_n sao cho khi xóa
    theo đúng thứ tự đó, mọi lượt xóa đều hợp lệ." Đây tương đương
    1 CSP với domain {0..n-1} cho mỗi biến và ràng buộc ALL-DIFFERENT
    + ràng buộc động, nhưng dễ code và dễ giải thích hơn.
    """

    def __init__(self, board: Board):
        self.board = board
        self.variables = board.find_all_pairs()  # mỗi cặp = 1 biến

    def is_consistent(self, assigned_order, candidate_pair):
        """
        Kiểm tra ràng buộc: nếu thêm candidate_pair vào CUỐI danh sách
        đã gán (assigned_order), liệu candidate_pair có còn nối được
        trên bàn cờ SAU KHI xóa hết các cặp trong assigned_order không?

        assigned_order: list các cặp ĐÃ được gán thứ tự xóa trước đó
                        (theo đúng thứ tự đã chọn).
        candidate_pair: cặp đang xét có nên gán làm "lượt tiếp theo".
        """
        sim_board = self.board.clone()
        for (r1, c1, r2, c2) in assigned_order:
            sim_board.remove(r1, c1, r2, c2)

        r1, c1, r2, c2 = candidate_pair
        return can_connect(sim_board, r1, c1, r2, c2)

    def is_complete(self, assigned_order):
        return len(assigned_order) == len(self.variables)
