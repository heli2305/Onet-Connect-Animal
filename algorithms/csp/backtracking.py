"""
backtracking.py - Backtracking Search (cho CSP)
=================================================
Nhóm: Constraint Satisfaction Problem (CSP)
Bài toán áp dụng: xem algorithms/csp/csp_problem.py để hiểu cách map
bài toán "giải bàn cờ" thành 1 CSP (biến = cặp thú, domain = thứ tự
xóa, ràng buộc = ALL-DIFFERENT + "nối được tại thời điểm xóa").

Ý tưởng Backtracking (đúng pseudocode chuẩn trong sách AI):
  - Thử gán giá trị cho 1 biến chưa gán (ở đây: CHỌN 1 cặp chưa được
    xếp thứ tự để xếp vào VỊ TRÍ TIẾP THEO trong thứ tự xóa).
  - Kiểm tra ràng buộc (is_consistent): cặp đó có còn nối được trên
    bàn cờ hiện tại (sau khi đã xóa các cặp gán trước) không?
  - Nếu hợp lệ -> gán, rồi ĐỆ QUY xử lý biến tiếp theo.
  - Nếu đến 1 bước nào đó KHÔNG CÒN biến nào hợp lệ để gán tiếp
    -> QUAY LẠI (backtrack): hủy gán biến vừa rồi, thử biến khác.

Độ phức tạp: trường hợp xấu nhất O(n!) (n = số cặp), vì backtracking
không có thông tin định hướng (khác Forward Checking / AC-3 sẽ cắt
bớt domain trước khi thử). Đây chính là động lực dẫn đến AC-3 trong
đồ án này.
"""

from algorithms.base import SearchLogger
from algorithms.csp.csp_problem import PikachuCSP
from game.board import Board


def backtracking_search(board: Board, max_steps=200000):
    """
    Chạy Backtracking Search để tìm 1 THỨ TỰ xóa hợp lệ cho toàn bộ
    các cặp trên bàn.

    Trả về: SearchResult (xem algorithms/base.py). actions = list thứ
    tự cặp đã chọn (nếu success=True, đây chính là lời giải dọn sạch
    bàn).
    """
    logger = SearchLogger("Backtracking (CSP)")
    csp = PikachuCSP(board)
    remaining_variables = list(csp.variables)

    step_counter = [0]  # dùng list để có thể sửa giá trị trong hàm đệ quy lồng

    def backtrack(assigned_order, unassigned):
        step_counter[0] += 1
        if step_counter[0] > max_steps:
            return None  # vượt quá giới hạn bước, dừng để tránh chạy quá lâu

        logger.on_expand()

        if csp.is_complete(assigned_order):
            return assigned_order  # đã gán hết mọi biến -> tìm được lời giải

        for i, candidate in enumerate(unassigned):
            logger.on_generate()
            if csp.is_consistent(assigned_order, candidate):
                # Tạo bản chụp của bàn cờ sau khi xóa cặp candidate này
                assigned_board = board.clone()
                for (r1, c1, r2, c2) in assigned_order + [candidate]:
                    assigned_board.remove(r1, c1, r2, c2)

                logger.log(
                    f"Gán cặp {candidate} vào lượt {len(assigned_order)} "
                    f"(còn {len(unassigned) - 1} biến chưa gán)",
                    state=assigned_board
                )
                new_assigned = assigned_order + [candidate]
                new_unassigned = unassigned[:i] + unassigned[i + 1:]

                result = backtrack(new_assigned, new_unassigned)
                if result is not None:
                    return result

                # Tạo bản chụp của bàn cờ trước khi gán cặp candidate này (khi backtrack)
                backtrack_board = board.clone()
                for (r1, c1, r2, c2) in assigned_order:
                    backtrack_board.remove(r1, c1, r2, c2)

                logger.log(
                    f"  Quay lại (backtrack): bỏ gán cặp {candidate}",
                    state=backtrack_board
                )

        return None  # không có candidate nào hợp lệ -> báo thất bại để quay lại

    solution = backtrack([], remaining_variables)

    if solution is not None:
        logger.log(f"Tìm được thứ tự xóa hợp lệ cho toàn bộ {len(solution)} cặp!")
        return logger.finalize(True, actions=solution, states=[], cost=len(solution))
    else:
        logger.log("Không tìm được thứ tự xóa hợp lệ (hoặc vượt quá giới hạn bước).")
        return logger.finalize(False)
