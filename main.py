"""
main.py - Giao diện chính game Nối Thú (Pikachu)
=================================================
Chỉ dùng: pygame + các file game/ và algorithms/ của dự án.
Layout 4 vùng:
  - Trái  : nút chọn thuật toán
  - Giữa trên : bàn cờ
  - Giữa dưới : kết quả chạy
  - Phải  : log từng bước
"""

import sys
import threading
import ctypes

# Kích hoạt chế độ DPI-aware cho Windows
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2) # PROCESS_PER_MONITOR_DPI_AWARE
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

import pygame

sys.path.insert(0, ".")
from game.state import make_initial_state
from game.rules import find_path
from game.visualizer import Visualizer, cell_rect, SCREEN_W, SCREEN_H, LEFT_W, RIGHT_W, BOARD_H
from algorithms.informed.astar import astar
from algorithms.csp.backtracking import backtracking_search

# ─────────────────────────────────────────────
# DANH SÁCH THUẬT TOÁN
# mỗi phần tử: (tên hiển thị, hàm gọi)
# Khi implement xong 1 thuật toán thì thêm vào đây
# ─────────────────────────────────────────────
def run_astar(state):
    return astar(state)

def run_backtracking(state):
    return backtracking_search(state.board)

# Placeholder cho các thuật toán chưa implement
def chua_implement(state):
    from algorithms.base import SearchLogger
    logger = SearchLogger("Chưa implement")
    logger.log("Thuật toán này chưa được code.")
    logger.log("Tạm thời dùng A* thay thế.")
    return astar(state)

ALGORITHMS = [
    # (tên,                  hàm chạy)
    # Uninformed Search
    ("BFS",                  chua_implement),
    ("UCS",                  chua_implement),
    # Informed Search
    ("A* Search",            run_astar),
    ("Greedy",               chua_implement),
    # Local Search
    ("Hill-Climbing",        chua_implement),
    ("Sim. Annealing",       chua_implement),
    # Complicated Search
    ("AND-OR Search",        chua_implement),
    ("Partial Observable",   chua_implement),
    # CSP
    ("Backtracking (CSP)",   run_backtracking),
    ("AC-3",                 chua_implement),
    # Đối kháng
    ("Minimax",              chua_implement),
    ("Alpha-Beta",           chua_implement),
]


# ─────────────────────────────────────────────
# VÒNG LẶP CHÍNH
# ─────────────────────────────────────────────
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Nối Thú")
    clock = pygame.time.Clock()

    viz = Visualizer()

    # ── Trạng thái game ──────────────────────────────────────────
    seed  = 42
    state = make_initial_state(rows=6, cols=6, seed=seed)

    selected_cell = None     # ô người chơi đang chọn, dạng (r, c)
    path_cells    = []       # danh sách ô trên đường nối đang hiển thị
    path_countdown = 0       # đếm ngược frame để ẩn đường nối
    path_animal_id = 0       # loại thú đang hiển thị đường nối

    # ── Trạng thái thuật toán ─────────────────────────────────────
    selected_algo = 0        # index thuật toán đang chọn
    is_running    = False    # đang chạy thuật toán hay không
    result        = None     # SearchResult sau khi chạy xong
    is_analysis_mode = False # Đang ở chế độ phân tích hay không
    analysis_step    = 0     # Bước phân tích hiện tại
    search_start_idx = 0     # Vị trí dòng log bắt đầu thuật toán

    # ── Log panel phải ────────────────────────────────────────────
    log_lines  = ["Chọn thuật toán và nhấn [Chạy AI]."]
    log_scroll = 0           # số dòng đã cuộn

    # ── Queue animation auto-solve ────────────────────────────────
    anim_queue   = []        # list action chờ thực hiện
    anim_timer   = 0         # đếm frame giữa 2 bước animation
    ANIM_DELAY   = 30        # số frame giữa 2 bước (30 frame ≈ 0.5 giây)

    def new_game(next_seed=False):
        """Reset về bàn mới."""
        nonlocal state, selected_cell, path_cells, path_countdown, seed, path_animal_id
        nonlocal result, anim_queue, anim_timer, log_lines, log_scroll
        nonlocal is_analysis_mode, analysis_step
        if next_seed:
            seed += 1
        state          = make_initial_state(rows=6, cols=6, seed=seed)
        selected_cell  = None
        path_cells     = []
        path_countdown = 0
        path_animal_id = 0
        result         = None
        anim_queue     = []
        anim_timer     = 0
        log_lines      = [f"Bàn mới — seed={seed}"]
        log_scroll     = 0
        is_analysis_mode = False
        analysis_step    = 0

    def stop_search():
        """Dừng việc tìm kiếm và hoạt ảnh."""
        nonlocal anim_queue, path_cells, result, log_lines, is_running
        anim_queue = []
        path_cells = []
        result = None
        is_running = False
        log_lines.append("Đã dừng hoạt ảnh / tìm kiếm.")

    def start_algorithm():
        """Chạy thuật toán trong thread riêng (không đơ UI)."""
        nonlocal is_running, result, anim_queue, log_lines, log_scroll
        nonlocal is_analysis_mode, analysis_step, search_start_idx

        name, func = ALGORITHMS[selected_algo]
        log_lines.append(f"Bắt đầu: {name}")
        is_running = True
        is_analysis_mode = False
        analysis_step = 0
        search_start_idx = len(log_lines)

        def worker():
            nonlocal result, anim_queue, log_lines, log_scroll, is_running
            r = func(state)
            result = r
            # Ghi log vào panel phải
            for msg in r.log_messages:
                log_lines.append(msg)
            log_scroll = max(0, len(log_lines) - ((SCREEN_H - 80) // 15))
            if r.success:
                log_lines.append(f"Xong! Cost={r.cost}, Nodes={r.expanded_nodes}")
                anim_queue = list(r.actions)
            else:
                log_lines.append("Không tìm được lời giải.")
            is_running = False

        threading.Thread(target=worker, daemon=True).start()

    # ─────────────────────────────────────────────────────────────
    # VÒNG LẶP CHÍNH
    # ─────────────────────────────────────────────────────────────
    while True:
        clock.tick(60)

        # ── Xử lý sự kiện ────────────────────────────────────────
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                if event.key == pygame.K_UP:
                    log_scroll = max(0, log_scroll - 2)
                if event.key == pygame.K_DOWN:
                    log_scroll = min(len(log_lines) - 1, log_scroll + 2)
                if event.key == pygame.K_LEFT:
                    if is_analysis_mode and result and hasattr(result, "search_steps") and result.search_steps:
                        analysis_step = max(0, analysis_step - 1)
                if event.key == pygame.K_RIGHT:
                    if is_analysis_mode and result and hasattr(result, "search_steps") and result.search_steps:
                        analysis_step = min(len(result.search_steps) - 1, analysis_step + 1)
                if event.key == pygame.K_n:
                    new_game(next_seed=True)
                if event.key == pygame.K_s:
                    stop_search()

            # Cuộn chuột trên panel log
            if event.type == pygame.MOUSEWHEEL:
                mx, _ = pygame.mouse.get_pos()
                if mx > SCREEN_W - RIGHT_W:
                    log_scroll = max(0, log_scroll - event.y * 2)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos

                # --- Click chọn thuật toán (panel trái) ---
                if mx < LEFT_W:
                    y = 32
                    for i, (name, _) in enumerate(ALGORITHMS):
                        btn = pygame.Rect(5, y, LEFT_W - 10, 30)
                        if btn.collidepoint(mx, my):
                            selected_algo = i
                            log_lines.append(f"Chọn: {name}")
                            break
                        y += 33

                # --- Click nút [Chạy AI] ---
                btn_run = pygame.Rect(5, SCREEN_H - 118, LEFT_W - 10, 34)
                if btn_run.collidepoint(mx, my) and not is_running:
                    new_game(next_seed=False)
                    start_algorithm()

                # --- Click nút [Bàn mới] ---
                btn_new = pygame.Rect(5, SCREEN_H - 78, LEFT_W - 10, 30)
                if btn_new.collidepoint(mx, my):
                    new_game(next_seed=True)

                # --- Click nút [Dừng] ---
                btn_stop = pygame.Rect(5, SCREEN_H - 42, LEFT_W - 10, 30)
                if btn_stop.collidepoint(mx, my):
                    stop_search()

                # --- Click nút [Chế độ Phân tích] ---
                btn_mode = pygame.Rect(5, 460, LEFT_W - 10, 30)
                if btn_mode.collidepoint(mx, my) and result and hasattr(result, "search_steps") and result.search_steps:
                    is_analysis_mode = not is_analysis_mode

                # --- Click các nút điều hướng phân tích [Trước] / [Sau] ---
                if is_analysis_mode and result and hasattr(result, "search_steps") and result.search_steps:
                    btn_prev = pygame.Rect(5, 535, (LEFT_W - 10) // 2 - 2, 28)
                    btn_next = pygame.Rect(5 + (LEFT_W - 10) // 2 + 2, 535, (LEFT_W - 10) // 2 - 2, 28)
                    if btn_prev.collidepoint(mx, my):
                        analysis_step = max(0, analysis_step - 1)
                    elif btn_next.collidepoint(mx, my):
                        analysis_step = min(len(result.search_steps) - 1, analysis_step + 1)

                # --- Click ô bàn cờ (chế độ tự chơi) ---
                if LEFT_W < mx < SCREEN_W - RIGHT_W and my < BOARD_H:
                    if not is_running and not anim_queue:
                        board = state.board
                        for r in range(board.rows):
                            for c in range(board.cols):
                                rc = cell_rect(board, r, c)
                                if rc.collidepoint(mx, my) and board.get(r,c) != 0:
                                    if selected_cell is None:
                                        selected_cell = (r, c)
                                    else:
                                        r1, c1 = selected_cell
                                        if (r1, c1) == (r, c):
                                            selected_cell = None
                                        elif board.get(r1,c1) == board.get(r,c):
                                            path = find_path(board, r1,c1, r,c)
                                            if path:
                                                path_cells    = path
                                                path_countdown = 25
                                                path_animal_id = board.get(r1, c1)
                                                state = state.apply_action((r1,c1,r,c))
                                                log_lines.append(f"Nối ({r1},{c1})↔({r},{c})")
                                                if state.is_goal():
                                                    log_lines.append("Dọn sạch bàn!")
                                            else:
                                                log_lines.append("Không nối được!")
                                            selected_cell = None
                                        else:
                                            selected_cell = (r, c)

        # ── Cập nhật animation ────────────────────────────────────
        if path_countdown > 0:
            path_countdown -= 1
            if path_countdown == 0:
                path_cells = []
                path_animal_id = 0

        if anim_queue and not is_running and not is_analysis_mode:
            anim_timer += 1
            if anim_timer >= ANIM_DELAY:
                anim_timer = 0
                action = anim_queue.pop(0)
                r1, c1, r2, c2 = action
                if state.board.get(r1, c1) != 0:
                    p = find_path(state.board, r1,c1, r2,c2)
                    if p:
                        path_cells     = p
                        path_countdown = 25
                        path_animal_id = state.board.get(r1, c1)
                    state = state.apply_action(action)

        # ── Chuẩn bị trạng thái hiển thị (Chế độ Phân tích) ──
        display_state = state
        active_log_idx = None
        if is_analysis_mode and result and hasattr(result, "search_steps") and result.search_steps:
            snapshot_board, _ = result.search_steps[analysis_step]
            if snapshot_board is not None:
                from game.state import GameState
                display_state = GameState(snapshot_board)
            active_log_idx = search_start_idx + analysis_step
            # Tự động cuộn để dòng log đang xét nằm chính giữa
            visible_lines = (SCREEN_H - 80) // 15
            log_scroll = max(0, active_log_idx - visible_lines // 2)

        # ── VẼ ───────────────────────────────────────────────────
        viz.draw(
            screen,
            display_state,
            selected_cell,
            path_cells,
            path_animal_id,
            result,
            log_lines,
            log_scroll,
            ALGORITHMS,
            selected_algo,
            is_running,
            is_analysis_mode=is_analysis_mode,
            analysis_step=analysis_step,
            active_log_idx=active_log_idx
        )

        # ════════════════════════════════════════════════════
        pygame.display.flip()


if __name__ == "__main__":
    # Cần dùng biến seed có thể thay đổi → dùng list 1 phần tử
    # (cách đơn giản nhất trong Python để sửa biến từ trong hàm lồng)
    main()
