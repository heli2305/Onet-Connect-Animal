import heapq
import itertools
from algorithms.base import SearchLogger, reconstruct_path

def greedy(initial_state):
    logger = SearchLogger("Greedy")
    came_from = {initial_state: None}
    counter = itertools.count()
    frontier = []

    def push(state):
        h = state.heuristic()
        tie_break = -len(state.get_actions())
        heapq.heappush(frontier, (h, tie_break, next(counter), state))

    push(initial_state)
    logger.on_generate(initial_state)
    h0 = initial_state.heuristic()
    logger.log(f"[Greedy] Bắt đầu | h0={h0} | Frontier:1", state=initial_state)

    if initial_state.is_goal():
        states, actions = reconstruct_path(came_from, initial_state)
        return logger.finalize(True, actions, states, cost=0)

    visited = set()

    while frontier:
        h_val, _, _, state = heapq.heappop(frontier)

        if state in visited:
            continue
        visited.add(state)
        logger.on_expand(state)

        prev = came_from.get(state)
        if prev:
            _, (r1, c1, r2, c2) = prev
            action_part = f"Nối:({r1},{c1})-({r2},{c2}) | "
        else:
            action_part = ""

        actions = state.get_actions()
        logger.log(
            f"[Mở rộng] {action_part}h={h_val:.2f} | Fron:{len(frontier)} | Reached:{len(visited)} | Child:{len(actions)}",
            state=state
        )

        if state.is_goal():
            logger.log(f"[Xong] Tìm thấy! Đã duyệt:{logger.expanded_nodes}")
            states, actions_path = reconstruct_path(came_from, state)
            return logger.finalize(True, actions_path, states, cost=len(actions_path))

        for action in state.get_actions():
            child = state.apply_action(action)
            if child in visited:
                continue
            if child not in came_from:
                came_from[child] = (state, action)
                push(child)
                logger.on_generate(child)

    logger.log("[Thất bại] Không tìm được lời giải.")
    return logger.finalize(False)
