"""
base.py
-------
Định nghĩa các cấu trúc dữ liệu DÙNG CHUNG cho toàn bộ 12 thuật toán,
để:
  1. Mọi thuật toán trả về kết quả CÙNG MỘT DẠNG (SearchResult)
     -> benchmark.py và visualizer.py không cần biết đang chạy
        thuật toán nào, chỉ cần đọc SearchResult.
  2. Mọi thuật toán ghi log CÙNG MỘT CÁCH (SearchLogger)
     -> khung "Quá trình các bước chạy" trên Pygame hiển thị
        đồng nhất cho cả 12 thuật toán.
"""

import time
from dataclasses import dataclass, field


@dataclass
class SearchResult:
    """Kết quả trả về CHUNG cho mọi thuật toán (đặt trong algorithms/*)."""

    success: bool                     # có tìm ra lời giải / dọn sạch bàn không
    actions: list = field(default_factory=list)   # list các action đã chọn, theo thứ tự
    states: list = field(default_factory=list)    # list các GameState đi qua (để animation)
    cost: int = 0                     # tổng chi phí lời giải (số bước)
    expanded_nodes: int = 0           # số node đã MỞ RỘNG (expand) - để so sánh hiệu năng
    generated_nodes: int = 0          # số node đã SINH RA (generate) - để so sánh hiệu năng
    time_seconds: float = 0.0         # thời gian chạy (đo bằng time.perf_counter)
    algorithm_name: str = ""          # tên thuật toán, để hiển thị trong bảng so sánh
    log_messages: list = field(default_factory=list)  # log từng bước, dạng text
    search_steps: list = field(default_factory=list)  # các bước tìm kiếm để phân tích, chứa (board_snapshot, message)


class SearchLogger:
    """
    Logger nhỏ dùng trong MỌI thuật toán để vừa đo thời gian / số node,
    vừa sinh ra các dòng log cho khung "Quá trình các bước chạy".

    Cách dùng trong 1 thuật toán (ví dụ bfs.py):

        logger = SearchLogger("BFS")
        ...
        logger.on_expand(state)              # mỗi khi lấy 1 node ra khỏi frontier để xét
        logger.on_generate(child_state)       # mỗi khi sinh ra 1 node con
        logger.log(f"Bước {k}: chọn cặp {action}")
        ...
        result = logger.finalize(success=True, actions=..., states=..., cost=...)
    """

    def __init__(self, algorithm_name: str):
        self.algorithm_name = algorithm_name
        self._start_time = time.perf_counter()
        self.expanded_nodes = 0
        self.generated_nodes = 0
        self.log_messages = []
        self.search_steps = []

    def on_expand(self, state=None):
        self.expanded_nodes += 1

    def on_generate(self, state=None):
        self.generated_nodes += 1

    def log(self, message: str, state=None):
        self.log_messages.append(message)
        # Lưu snapshot của bàn cờ (clone để tránh bị thay đổi trạng thái sau đó)
        snapshot = None
        if state is not None:
            if hasattr(state, "board") and hasattr(state.board, "clone"):
                snapshot = state.board.clone()
            elif hasattr(state, "clone"):
                snapshot = state.clone()
        self.search_steps.append((snapshot, message))

    def finalize(self, success, actions=None, states=None, cost=0) -> SearchResult:
        elapsed = time.perf_counter() - self._start_time
        return SearchResult(
            success=success,
            actions=actions or [],
            states=states or [],
            cost=cost,
            expanded_nodes=self.expanded_nodes,
            generated_nodes=self.generated_nodes,
            time_seconds=elapsed,
            algorithm_name=self.algorithm_name,
            log_messages=self.log_messages,
            search_steps=self.search_steps,
        )


def reconstruct_path(came_from, last_state):
    """
    Hàm tiện ích DÙNG CHUNG: truy ngược dict came_from (giống pseudocode
    sách Russell & Norvig) để lấy ra list state và list action từ
    state ban đầu -> last_state.

    came_from[state] = (state_cha, action_dẫn_tới_state)
    Trả về: (list_states, list_actions) theo đúng thứ tự đi từ đầu -> cuối.
    """
    states = [last_state]
    actions = []
    cur = last_state
    while came_from.get(cur) is not None:
        parent, action = came_from[cur]
        states.append(parent)
        actions.append(action)
        cur = parent
    states.reverse()
    actions.reverse()
    return states, actions
