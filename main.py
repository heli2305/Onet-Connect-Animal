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
from algorithms.LocalSearch.beam_search import beam_search
from algorithms.ConstraintSatisfactionProblems.backtracking import backtracking_search
from algorithms.ConstraintSatisfactionProblems.feedforward import feedforward_search
from algorithms.LocalSearch.hill_climbing import hill_climbing_search
from algorithms.AdversarialSearch.alpha_beta import alpha_beta_search_full

# DANH SÁCH THUẬT TOÁN

def run_bfs(state):
    return bfs(state)

def run_dfs(state):
    return dfs(state)

def run_astar(state):
    return astar(state)

def run_greedy(state):
    return greedy(state)

def run_beam_search(state):
    return beam_search(state)

def run_backtracking(state):
    return backtracking_search(state)

def run_feedforward(state):
    return feedforward_search(state)

def run_hill_climbing(state):
    return hill_climbing_search(state)

def run_alpha_beta(state):
    return alpha_beta_search_full(state)

ALGO_GROUPS = [
    {
        "name": "Uninformed search",
        "algos": [
            {"name": "BFS", "func": run_bfs},
            {"name": "DFS (FF)", "func": run_dfs}
        ]
    },
    {
        "name": "Informed search",
        "algos": [
            {"name": "A* Search", "func": run_astar},
            {"name": "Greedy (FF)", "func": run_greedy}
        ]
    },
    {
        "name": "Local search",
        "algos": [
            {"name": "Beam Search (FF)", "func": run_beam_search},
            {"name": "Hill Climbing", "func": run_hill_climbing}
        ]
    },
    {
        "name": "Searching in complex environments",
        "algos": []
    },
    {
        "name": "Constraint satisfaction problems",
        "algos": [
            {"name": "Backtracking (CSP)", "func": run_backtracking},
            {"name": "Feedforward", "func": run_feedforward}
        ]
    },
    {
        "name": "Adversarial search",
        "algos": [
            {"name": "Alpha-Beta Search", "func": run_alpha_beta}
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
            nonlocal result, anim_queue, log_lines, log_scroll, is_running
            r = func(state)
            result = r

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
                mx, _ = pygame.mouse.get_pos()
                if mx > SCREEN_W - RIGHT_W:
                    log_scroll = max(0, log_scroll - event.y * 2)

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
        if is_analysis_mode and result and hasattr(result, "search_steps") and result.search_steps:
            snapshot_board, _ = result.search_steps[analysis_step]
            if snapshot_board is not None:
                from game.state import GameState
                display_state = GameState(snapshot_board)
            active_log_idx = search_start_idx + analysis_step
            visible_lines = (SCREEN_H - 100) // LOG_LINE_H
            log_scroll = max(0, active_log_idx - visible_lines // 2)


        viz.draw(
            screen,
            display_state,
            selected_cell,
            path_cells,
            path_animal_id,
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
            active_log_idx=active_log_idx
        )

        pygame.display.flip()


if __name__ == "__main__":
    main()
