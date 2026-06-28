from collections import deque
from algorithms.base import SearchLogger
from game.state import GameState
from game.board import Board
import numpy as np


def get_components(board):
    visited = set()
    components = []

    for r in range(board.rows):
        for c in range(board.cols):
            if board.get(r, c) != 0 and (r, c) not in visited:
                comp = set()
                seen = {(r, c)}
                q = deque([(r, c)])
                while q:
                    cr, cc = q.popleft()
                    if board.get(cr, cc) != 0:
                        comp.add((cr, cc))
                        visited.add((cr, cc))
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nr, nc = cr + dr, cc + dc
                        if 0 <= nr < board.rows and 0 <= nc < board.cols and (nr, nc) not in seen:
                            seen.add((nr, nc))
                            q.append((nr, nc))
                if comp:
                    components.append(comp)

    return components


def make_sub_board(board, cells):
    sub = Board.__new__(Board)
    sub.rows = board.rows
    sub.cols = board.cols
    sub._rng = board._rng
    sub.board = np.zeros((board.rows, board.cols), dtype=int)
    for r, c in cells:
        sub.board[r][c] = board.board[r][c]
    return sub


def decompose(board):
    components = get_components(board)
    if len(components) <= 1:
        return [board]

    tile_to_comp = {}
    for i, comp in enumerate(components):
        for cell in comp:
            tile_to_comp[cell] = i

    for val in set(board.board.flatten()) - {0}:
        positions = [(r, c) for r in range(board.rows)
                     for c in range(board.cols) if board.get(r, c) == val]
        comps = {tile_to_comp[p] for p in positions}
        if len(comps) > 1:
            return [board]

    return [make_sub_board(board, comp) for comp in components]


def flatten_plan(plan):
    if plan is None or plan["type"] == "goal":
        return []
    if plan["type"] == "or":
        return [plan["action"]] + flatten_plan(plan["sub_plan"])
    if plan["type"] == "and":
        result = [plan["action"]]
        for sp in plan["sub_plans"]:
            result += flatten_plan(sp)
        return result
    return []


def or_search(state, path, logger):
    if state.is_goal():
        return {"type": "goal"}

    if state.key() in path:
        return None

    new_path = path | {state.key()}
    logger.on_expand(state)

    for action in state.get_actions():
        logger.on_generate(state)
        child = state.apply_action(action)
        result_states = decompose(child.board)
        r1, c1, r2, c2 = action

        if len(result_states) == 1:
            logger.log(f"[OR] ({r1},{c1})-({r2},{c2})", state=child.board)
            sub_plan = or_search(child, new_path, logger)
            if sub_plan is not None:
                return {"type": "or", "action": action, "sub_plan": sub_plan}

        else:
            logger.log(f"[AND] ({r1},{c1})-({r2},{c2}) | {len(result_states)} vùng", state=child.board)
            sub_plans = and_search([GameState(b) for b in result_states], new_path, logger)
            if sub_plans is not None:
                return {"type": "and", "action": action, "sub_plans": sub_plans}

    return None


def and_search(states, path, logger):
    plans = []
    for s in states:
        plan_s = or_search(s, path, logger)
        if plan_s is None:
            return None
        plans.append(plan_s)
    return plans


def and_or_search(initial_state):
    logger = SearchLogger("AND-OR Graph Search")
    total = initial_state.board.num_remaining_tiles() // 2
    logger.log(f"[AND-OR] Bắt đầu | {total} cặp", state=initial_state.board)

    plan = or_search(initial_state, set(), logger)

    if plan is None:
        logger.log("[Thất bại] Không tìm được kế hoạch.")
        return logger.finalize(False)

    actions = flatten_plan(plan)
    logger.log(f"[Xong] Kế hoạch: {len(actions)} bước")
    return logger.finalize(True, actions=actions, cost=len(actions))