import heapq
import itertools

from algorithms.base import SearchLogger, reconstruct_path
from game.state import GameState


def astar(initial_state: GameState):
    logger = SearchLogger("A*")

    came_from = {initial_state: None}
    g_cost = {initial_state: 0}
    counter = itertools.count()
    frontier = []

    def push(state, g):
        h = state.heuristic()
        f = g + h
        tie_break = -len(state.get_actions())  
        heapq.heappush(frontier, (f, tie_break, next(counter), state))

    push(initial_state, 0)
    logger.on_generate(initial_state)

    h0 = initial_state.heuristic()
    logger.log(f"[A*] Bắt đầu | h0={h0} | Frontier:1", state=initial_state)

    if initial_state.is_goal():
        logger.log("[Xong] Bàn cờ đã trống ngay từ đầu.")
        states, actions = reconstruct_path(came_from, initial_state)
        return logger.finalize(True, actions, states, cost=0)

    visited = set()

    while frontier:
        f_n, _, _, state = heapq.heappop(frontier)

        if state in visited:
            continue
        visited.add(state)

        logger.on_expand(state)
        g_n = g_cost[state]
        h_n = state.heuristic()

        prev = came_from.get(state)
        if prev:
            _, (r1, c1, r2, c2) = prev
            action_part = f"Nối:({r1},{c1})-({r2},{c2}) | "
        else:
            action_part = ""

        actions = state.get_actions()
        logger.log(
            f"[Mở rộng] {action_part}g={g_n} h={h_n} f={f_n} | Fron:{len(frontier)} | Reached:{len(visited)} | Child:{len(actions)}",
            state=state
        )

        if state.is_goal():
            logger.log(f"[Xong] Tối ưu! {g_n} bước | Đã duyệt:{logger.expanded_nodes}", state=state)
            states, actions = reconstruct_path(came_from, state)
            return logger.finalize(True, actions, states, cost=len(actions))

        for action in state.get_actions():
            child = state.apply_action(action)
            new_g = g_n + 1

            if child in visited:
                continue

            if child not in g_cost or new_g < g_cost[child]:
                g_cost[child] = new_g
                came_from[child] = (state, action)
                push(child, new_g)
                logger.on_generate(child)

    logger.log("[Thất bại] Đã duyệt hết không gian, không tìm được lời giải.")
    return logger.finalize(False)
