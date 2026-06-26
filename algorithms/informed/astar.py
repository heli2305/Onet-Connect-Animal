"""
astar.py - A* Search
=====================
Nhóm: Tìm kiếm có thông tin (Informed search)
Bài toán áp dụng: "Giải toàn bộ bàn cờ nối thú" (xem game/state.py)

Ý tưởng:
  - Giống UCS nhưng độ ưu tiên của 1 node trong frontier không chỉ
    dựa vào g(n) (chi phí đã đi từ gốc đến n) mà còn cộng thêm
    h(n) (ước lượng chi phí còn lại từ n đến goal):
        f(n) = g(n) + h(n)
  - Node có f(n) NHỎ NHẤT được mở rộng trước.
  - Heuristic dùng: h(n) = số cặp thú còn lại trên bàn (xem
    GameState.heuristic() trong game/state.py). Đây là heuristic
    ADMISSIBLE (không bao giờ đánh giá quá cao chi phí thật còn lại,
    vì trong điều kiện tốt nhất ta cần đúng "số cặp còn lại" bước
    để dọn sạch bàn, không thể ít hơn).

LƯU Ý QUAN TRỌNG (rút ra từ thực nghiệm, ghi rõ để giải thích khi
bảo vệ đồ án): với bài toán này, MỌI state ở cùng độ sâu g luôn có
CÙNG MỘT GIÁ TRỊ h (vì mỗi action luôn làm giảm đúng 1 cặp, không
phụ thuộc action nào được chọn). Hệ quả: f = g + h là HẰNG SỐ tại
mỗi mức độ sâu => nếu chỉ dùng (f, FIFO) để sắp hàng đợi, A* sẽ mở
rộng node theo đúng thứ tự độ sâu giống BFS, không có lợi thế gì.

=> Cách khắc phục TRONG ĐỒ ÁN NÀY: giữ nguyên h (vẫn admissible, vẫn
đảm bảo lời giải tối ưu) nhưng thêm 1 TIÊU CHÍ PHỤ (tie-breaker) khi
2 node có cùng f: ưu tiên mở rộng state có ÍT ACTION KHẢ THI HƠN
(state "gần bị kẹt" hơn, nên giải quyết sớm để tránh dồn việc khó
về cuối). Tiêu chí phụ này KHÔNG làm thay đổi tính admissible của h,
chỉ ảnh hưởng THỨ TỰ mở rộng trong cùng 1 mức f - giúp A* mở rộng
ít node hơn BFS trong thực nghiệm, dù vẫn đảm bảo tìm ra lời giải
với số bước tối ưu (cost nhỏ nhất).

Độ phức tạp: vẫn O(b^d) trong trường hợp xấu nhất, nhưng heuristic +
tie-breaker giúp giảm số node thực tế cần mở rộng so với BFS/UCS.
"""

import heapq
import itertools

from algorithms.base import SearchLogger, reconstruct_path
from game.state import GameState


def astar(initial_state: GameState):
    """
    Chạy A* trên bài toán "giải toàn bộ bàn cờ".
    Trả về: SearchResult (xem algorithms/base.py)
    """
    logger = SearchLogger("A*")

    came_from = {initial_state: None}
    g_cost = {initial_state: 0}   # g(n) = số bước đã đi từ gốc đến n

    # heapq so sánh tuple (f, tie_break, counter, state). Counter để
    # heapq luôn so sánh được (tránh lỗi so sánh trực tiếp 2 GameState).
    # tie_break = số action khả thi tại state đó (ưu tiên state "gần
    # kẹt" - ít action hơn - được mở rộng trước, xem giải thích ở trên).
    counter = itertools.count()
    frontier = []

    def push(state, g):
        h = state.heuristic()
        f = g + h
        tie_break = len(state.get_actions())
        heapq.heappush(frontier, (f, tie_break, next(counter), state))

    push(initial_state, 0)
    logger.on_generate(initial_state)

    if initial_state.is_goal():
        logger.log("Bàn cờ đã trống ngay từ đầu.")
        states, actions = reconstruct_path(came_from, initial_state)
        return logger.finalize(True, actions, states, cost=0)

    visited = set()

    while frontier:
        f_n, tie_break, _, state = heapq.heappop(frontier)

        if state in visited:
            continue
        visited.add(state)

        logger.on_expand(state)
        g_n = g_cost[state]
        h_n = state.heuristic()
        logger.log(
            f"Mở rộng node: g={g_n}, h={h_n}, f={f_n}, "
            f"số action khả thi={tie_break} "
            f"(còn {state.board.num_remaining_tiles()} ô)",
            state=state
        )

        if state.is_goal():
            logger.log("  -> Đây là goal! Dừng tìm kiếm.")
            states, actions = reconstruct_path(came_from, state)
            return logger.finalize(True, actions, states, cost=len(actions))

        for action in state.get_actions():
            child = state.apply_action(action)
            new_g = g_n + 1  # mỗi action chi phí 1

            if child in visited:
                continue

            if child not in g_cost or new_g < g_cost[child]:
                g_cost[child] = new_g
                came_from[child] = (state, action)
                push(child, new_g)
                logger.on_generate(child)

    logger.log("Đã duyệt hết không gian trạng thái, không tìm được lời giải.")
    return logger.finalize(False)
