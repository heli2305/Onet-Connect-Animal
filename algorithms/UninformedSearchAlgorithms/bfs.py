from collections import deque
from algorithms.base import SearchLogger, reconstruct_path


def bfs(initial_state):
    logger = SearchLogger("BFS")
    total_pairs = initial_state.board.num_remaining_tiles() // 2
    logger.log(f"[BFS] Bắt đầu | Frontier:1 | Cặp còn:{total_pairs}", state=initial_state)

    if initial_state.is_goal():
        return logger.finalize(True, [], [initial_state], 0)

    queue = deque([(initial_state, 0)])
    visited = {initial_state}
    came_from = {initial_state: None}

    logger.on_generate(initial_state)
    current_depth = -1

    while queue:
        state, depth = queue.popleft()
        logger.on_expand(state)

        if depth > current_depth:
            current_depth = depth
            logger.log(f"--- Depth = {current_depth} ---")

        prev = came_from.get(state)
        if prev:
            _, (r1, c1, r2, c2) = prev
            action_part = f"Nối:({r1},{c1})-({r2},{c2}) | "
        else:
            action_part = ""
        actions = state.get_actions()
        logger.log(
            f"[Mở rộng] {action_part}Fron:{len(queue)} | Reached:{len(visited)} | Child:{len(actions)}",
            state=state
        )

        for action in actions:
            child = state.apply_action(action)
            if child not in visited:
                visited.add(child)
                came_from[child] = (state, action)
                
                if child.is_goal():
                    logger.log(f"[Xong] Tìm thấy sau {logger.expanded_nodes + 1} bước!")
                    path_states, path_actions = reconstruct_path(came_from, child)
                    return logger.finalize(True, path_actions, path_states, cost=len(path_actions))
                
                queue.append((child, depth + 1))
                logger.on_generate(child)

    logger.log("[Thất bại] Queue rỗng, không tìm được lời giải.")
    return logger.finalize(False)
