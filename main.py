import sys
import threading
import ctypes

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

import pygame

sys.path.insert(0, ".")
from game.state import make_initial_state
from game.rules import find_path
from game.visualizer import Visualizer, cell_rect, SCREEN_W, SCREEN_H, LEFT_W, RIGHT_W, BOARD_H, LOG_LINE_H
from algorithms.InformedSearchAlgorithms.astar import astar
from algorithms.UninformedSearchAlgorithms.bfs import bfs
from algorithms.UninformedSearchAlgorithms.dfs import dfs
from algorithms.InformedSearchAlgorithms.greedy import greedy
from algorithms.LocalSearch.local_beam import local_beam_search
from algorithms.ConstraintSatisfactionProblems.backtracking import backtracking_search
from algorithms.ConstraintSatisfactionProblems.forwardchecking import forwardchecking_search
from algorithms.LocalSearch.hill_climbing import hill_climbing_search
from algorithms.AdversarialSearch.alpha_beta import alpha_beta_search_full
from algorithms.AdversarialSearch.minimax import minimax_search_full
from algorithms.SearchingInComplexEnvironments.and_or import and_or_search
from algorithms.SearchingInComplexEnvironments.partial_observable import partial_observable_search

# DANH SÁCH THUẬT TOÁN

def run_bfs(state):
    return bfs(state)

def run_dfs(state):
    return dfs(state)

def run_astar(state):
    return astar(state)

def run_greedy(state):
    return greedy(state)

def run_local_beam(state):
    return local_beam_search(state)

def run_backtracking(state):
    return backtracking_search(state)

def run_forwardchecking(state):
    return forwardchecking_search(state)

def run_hill_climbing(state):
    return hill_climbing_search(state)

def run_alpha_beta(state):
    return alpha_beta_search_full(state)

def run_minimax(state):
    return minimax_search_full(state, depth_limit=4)

def run_partial_observable(state):
    return partial_observable_search(state)

ALGO_GROUPS = [
    {
        "name": "Uninformed search",
        "algos": [
            {"name": "BFS", "func": run_bfs},
            {"name": "DFS", "func": run_dfs}
        ]
    },
    {
        "name": "Informed search",
        "algos": [
            {"name": "A* Search", "func": run_astar},
            {"name": "Greedy", "func": run_greedy}
        ]
    },
    {
        "name": "Local search",
        "algos": [
            {"name": "Local Beam Search", "func": run_local_beam},
            {"name": "Hill Climbing", "func": run_hill_climbing}
        ]
    },
    {
        "name": "Searching in complex environments",
        "algos": [
            {"name": "AND-OR Graph Search", "func": and_or_search},
            {"name": "Partial Observable", "func": run_partial_observable}
        ]
    },
    {
        "name": "Constraint satisfaction problems",
        "algos": [
            {"name": "Backtracking", "func": run_backtracking},
            {"name": "Forward Checking", "func": run_forwardchecking}
        ]
    },
    {
        "name": "Adversarial search",
        "algos": [
            {"name": "Minimax", "func": run_minimax},
            {"name": "Alpha-Beta", "func": run_alpha_beta}
        ]
    }
]


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Nối Thú")
    clock = pygame.time.Clock()

    viz = Visualizer()

    seed  = 42
    state = make_initial_state(rows=6, cols=6, seed=seed)

    selected_cell = None     
    path_cells    = []       
    path_countdown = 0       
    path_animal_id = 0       

    # Trạng thái thuật toán 
    selected_group_idx = 0
    selected_algo_idx  = 0
    opened_group       = 0
    is_running         = False    
    result        = None     
    is_analysis_mode = False 
    analysis_step    = 0     
    search_start_idx = 0     
    active_bottom_tab = 0
    run_history = []
    comparison_scroll = 0
    chart_metric = 0
    initial_state_for_analysis = state


    # Log
    log_lines  = ["Chọn thuật toán và nhấn [Chạy AI]."]
    log_scroll = 0          

    # Queue animation
    anim_queue   = []        
    anim_timer   = 0         
    ANIM_DELAY   = 30        

    def new_game(next_seed=False):
        nonlocal state, selected_cell, path_cells, path_countdown, seed, path_animal_id
        nonlocal result, anim_queue, anim_timer, log_lines, log_scroll
        nonlocal is_analysis_mode, analysis_step
        nonlocal run_history, active_bottom_tab, comparison_scroll, initial_state_for_analysis
        if next_seed:
            seed += 1
            run_history = []
            active_bottom_tab = 0
            comparison_scroll = 0
        state          = make_initial_state(rows=6, cols=6, seed=seed)
        initial_state_for_analysis = state
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
        nonlocal anim_queue, path_cells, result, log_lines, is_running
        anim_queue = []
        path_cells = []
        result = None
        is_running = False
        log_lines.append("Đã dừng hoạt ảnh / tìm kiếm.")

    def start_algorithm():
        nonlocal is_running, result, anim_queue, log_lines, log_scroll
        nonlocal is_analysis_mode, analysis_step, search_start_idx

        algo = ALGO_GROUPS[selected_group_idx]["algos"][selected_algo_idx]
        name = algo["name"]
        func = algo["func"]
        log_lines.append(f"Bắt đầu: {name}")
        is_running = True
        is_analysis_mode = False
        analysis_step = 0
        search_start_idx = len(log_lines)

        def worker():
            nonlocal result, anim_queue, log_lines, log_scroll, is_running, run_history
            r = func(state)
            result = r
            run_history.append(r)

            for msg in r.log_messages:
                log_lines.append(msg)
            log_scroll = max(0, len(log_lines) - ((SCREEN_H - 100) // LOG_LINE_H))
            if r.success:
                log_lines.append(f"Xong! Cost={r.cost}, Nodes={r.expanded_nodes}")
                anim_queue = list(r.actions)
            else:
                log_lines.append("Không tìm được lời giải.")
            is_running = False

        threading.Thread(target=worker, daemon=True).start()

    def start_compare_group():
        nonlocal is_running, run_history, active_bottom_tab, log_lines, log_scroll
        group = ALGO_GROUPS[selected_group_idx]
        log_lines.append(f"So sánh nhóm: {group['name']}...")
        is_running = True
        run_history = []
        active_bottom_tab = 1

        def worker():
            nonlocal is_running, run_history, log_lines, log_scroll
            for algo in group["algos"]:
                name = algo["name"]
                func = algo["func"]
                log_lines.append(f"-> Đang chạy {name}...")
                log_scroll = max(0, len(log_lines) - ((SCREEN_H - 100) // LOG_LINE_H))
                init_state = make_initial_state(rows=6, cols=6, seed=seed)
                try:
                    r = func(init_state)
                    r.algorithm_name = name
                    run_history.append(r)
                    log_lines.append(f"   {name}: {'Thành công' if r.success else 'Thất bại'} ({r.time_seconds*1000:.1f} ms)")
                except Exception as e:
                    log_lines.append(f"   {name}: Lỗi: {str(e)}")
                log_scroll = max(0, len(log_lines) - ((SCREEN_H - 100) // LOG_LINE_H))
            log_lines.append("Hoàn thành so sánh nhóm!")
            log_scroll = max(0, len(log_lines) - ((SCREEN_H - 100) // LOG_LINE_H))
            is_running = False

        threading.Thread(target=worker, daemon=True).start()

    def start_compare_all():
        nonlocal is_running, run_history, active_bottom_tab, log_lines, log_scroll
        log_lines.append("So sánh tất cả các nhóm thuật toán...")
        is_running = True
        run_history = []
        active_bottom_tab = 1

        def worker():
            nonlocal is_running, run_history, log_lines, log_scroll
            for group in ALGO_GROUPS:
                for algo in group["algos"]:
                    name = algo["name"]
                    func = algo["func"]
                    log_lines.append(f"-> Đang chạy {name}...")
                    log_scroll = max(0, len(log_lines) - ((SCREEN_H - 100) // LOG_LINE_H))
                    init_state = make_initial_state(rows=6, cols=6, seed=seed)
                    try:
                        r = func(init_state)
                        r.algorithm_name = name
                        run_history.append(r)
                        log_lines.append(f"   {name}: {'Thành công' if r.success else 'Thất bại'} ({r.time_seconds*1000:.1f} ms)")
                    except Exception as e:
                        log_lines.append(f"   {name}: Lỗi: {str(e)}")
                    log_scroll = max(0, len(log_lines) - ((SCREEN_H - 100) // LOG_LINE_H))
            log_lines.append("Hoàn thành so sánh tất cả!")
            log_scroll = max(0, len(log_lines) - ((SCREEN_H - 100) // LOG_LINE_H))
            is_running = False

        threading.Thread(target=worker, daemon=True).start()


    while True:
        clock.tick(60)

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

            if event.type == pygame.MOUSEWHEEL:
                mx, my = pygame.mouse.get_pos()
                if mx > SCREEN_W - RIGHT_W:
                    log_scroll = max(0, log_scroll - event.y * 2)
                elif LEFT_W + 410 < mx < SCREEN_W - RIGHT_W and my > BOARD_H:
                    comparison_scroll = max(0, comparison_scroll - event.y)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos

                if mx < LEFT_W:
                    y = 48
                    clicked_item = False
                    for g_idx, group in enumerate(ALGO_GROUPS):
                        header_rect = pygame.Rect(5, y, LEFT_W - 10, 36)
                        if header_rect.collidepoint(mx, my):
                            if opened_group == g_idx:
                                opened_group = None
                            else:
                                opened_group = g_idx
                            clicked_item = True
                            break
                        
                        y += 40
                        if opened_group == g_idx:
                            if not group["algos"]:
                                y += 24
                            else:
                                for a_idx, algo in enumerate(group["algos"]):
                                    item_rect = pygame.Rect(20, y, LEFT_W - 25, 30)
                                    if item_rect.collidepoint(mx, my):
                                        selected_group_idx = g_idx
                                        selected_algo_idx = a_idx
                                        log_lines.append(f"Chọn: {algo['name']}")
                                        clicked_item = True
                                        break
                                    y += 34
                            if clicked_item:
                                break


                btn_run = pygame.Rect(5, SCREEN_H - 158, LEFT_W - 10, 38)
                if btn_run.collidepoint(mx, my) and not is_running:
                    new_game(next_seed=False)
                    start_algorithm()

                btn_new = pygame.Rect(5, SCREEN_H - 108, LEFT_W - 10, 38)
                if btn_new.collidepoint(mx, my):
                    new_game(next_seed=True)

                btn_stop = pygame.Rect(5, SCREEN_H - 58, LEFT_W - 10, 38)
                if btn_stop.collidepoint(mx, my):
                    stop_search()

                btn_mode = pygame.Rect(5, 520, LEFT_W - 10, 34)
                if btn_mode.collidepoint(mx, my) and result and hasattr(result, "search_steps") and result.search_steps:
                    is_analysis_mode = not is_analysis_mode

                if is_analysis_mode and result and hasattr(result, "search_steps") and result.search_steps:
                    btn_prev = pygame.Rect(5, 600, (LEFT_W - 10) // 2 - 2, 32)
                    btn_next = pygame.Rect(5 + (LEFT_W - 10) // 2 + 2, 600, (LEFT_W - 10) // 2 - 2, 32)
                    if btn_prev.collidepoint(mx, my):
                        analysis_step = max(0, analysis_step - 1)
                    elif btn_next.collidepoint(mx, my):
                        analysis_step = min(len(result.search_steps) - 1, analysis_step + 1)

                if LEFT_W < mx < SCREEN_W - RIGHT_W and BOARD_H < my < BOARD_H + 38:
                    tab0_rect = pygame.Rect(LEFT_W + 12, BOARD_H + 10, 140, 28)
                    tab1_rect = pygame.Rect(LEFT_W + 162, BOARD_H + 10, 150, 28)
                    btn_cgroup = pygame.Rect(LEFT_W + 380, BOARD_H + 10, 140, 28)
                    btn_call = pygame.Rect(LEFT_W + 530, BOARD_H + 10, 150, 28)
                    
                    if tab0_rect.collidepoint(mx, my):
                        active_bottom_tab = 0
                    elif tab1_rect.collidepoint(mx, my):
                        active_bottom_tab = 1
                    elif active_bottom_tab == 1 and btn_cgroup.collidepoint(mx, my) and not is_running:
                        new_game(next_seed=False)
                        start_compare_group()
                    elif active_bottom_tab == 1 and btn_call.collidepoint(mx, my) and not is_running:
                        new_game(next_seed=False)
                        start_compare_all()

                if active_bottom_tab == 1 and LEFT_W < mx < SCREEN_W - RIGHT_W and BOARD_H + 48 < my < BOARD_H + 72:
                    toggles = [
                        pygame.Rect(LEFT_W + 12, BOARD_H + 48, 110, 24),
                        pygame.Rect(LEFT_W + 127, BOARD_H + 48, 110, 24),
                    ]
                    for idx, rect in enumerate(toggles):
                        if rect.collidepoint(mx, my):
                            chart_metric = idx
                            break

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

        display_state = state
        active_log_idx = None
        analysis_path_cells = []
        analysis_path_animal_id = 0

        if is_analysis_mode and result and hasattr(result, "search_steps") and result.search_steps:
            snapshot_board, msg = result.search_steps[analysis_step]
            if snapshot_board is not None:
                from game.state import GameState
                display_state = GameState(snapshot_board)
                
                # Trích xuất hiệu ứng nối thú động trong chế độ phân tích bằng regex
                import re
                coord_pattern = re.compile(r"\((\d+)\s*,\s*(\d+)\)[^\(]*\((\d+)\s*,\s*(\d+)\)")
                match = coord_pattern.search(msg)
                if match and not ("Bỏ Nối" in msg or "Quay lui" in msg):
                    r1, c1, r2, c2 = map(int, match.groups())
                    # Tránh vẽ đường nối trùng lặp nếu bước trước đó có cùng tọa độ
                    is_duplicate = False
                    if analysis_step > 0:
                        _, prev_msg = result.search_steps[analysis_step - 1]
                        prev_match = coord_pattern.search(prev_msg)
                        if prev_match:
                            pr1, pc1, pr2, pc2 = map(int, prev_match.groups())
                            if (pr1, pc1, pr2, pc2) == (r1, c1, r2, c2):
                                is_duplicate = True
                                
                    if not is_duplicate:
                        # Khôi phục trạng thái ban đầu của cặp thú để tìm đường nối
                        val = initial_state_for_analysis.board.get(r1, c1)
                        if val != 0:
                            board_prev = snapshot_board.clone()
                            board_prev.board[r1][c1] = val
                            board_prev.board[r2][c2] = val
                            analysis_path_cells = find_path(board_prev, r1, c1, r2, c2)
                            analysis_path_animal_id = val

            active_log_idx = search_start_idx + analysis_step
            visible_lines = (SCREEN_H - 100) // LOG_LINE_H
            log_scroll = max(0, active_log_idx - visible_lines // 2)


        viz.draw(
            screen,
            display_state,
            selected_cell if not is_analysis_mode else None,
            path_cells if not is_analysis_mode else analysis_path_cells,
            path_animal_id if not is_analysis_mode else analysis_path_animal_id,
            result,
            log_lines,
            log_scroll,
            ALGO_GROUPS,
            selected_group_idx,
            selected_algo_idx,
            opened_group,
            is_running,
            is_analysis_mode=is_analysis_mode,
            analysis_step=analysis_step,
            active_log_idx=active_log_idx,
            active_bottom_tab=active_bottom_tab,
            run_history=run_history,
            comparison_scroll=comparison_scroll,
            chart_metric=chart_metric
        )

        pygame.display.flip()


if __name__ == "__main__":
    main()
