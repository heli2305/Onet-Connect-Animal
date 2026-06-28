from algorithms.base import SearchLogger, reconstruct_path


def dfs(initial_state):
    logger = SearchLogger("DFS")
    total_pairs = initial_state.board.num_remaining_tiles() // 2
    logger.log(f"[DFS] Bắt đầu | Frontier:1 | Cặp còn:{total_pairs}", state=initial_state)

    stack = [initial_state]
    visited = set()
    came_from = {initial_state: None}
    logger.on_generate(initial_state)

    while stack:
        state = stack.pop()
        
        if state in visited:
            continue
        visited.add(state)
        logger.on_expand(state)

        if state.is_goal():
            logger.log(f"[Xong] Tìm thấy sau {logger.expanded_nodes} bước!")
            path_states, path_actions = reconstruct_path(came_from, state)
            return logger.finalize(True, path_actions, path_states, cost=len(path_actions))

        prev = came_from.get(state)
        if prev:
            _, (r1, c1, r2, c2) = prev
            action_part = f"Nối:({r1},{c1})-({r2},{c2}) | "
        else:
            action_part = ""
        
        actions = state.get_actions()
        logger.log(
            f"[Mở rộng] {action_part}Fron:{len(stack)} | Reached:{len(visited)} | Child:{len(actions)}",
            state=state
        )

        for action in actions:
            child = state.apply_action(action)
            if child not in visited:
                came_from[child] = (state, action)
                stack.append(child)
                logger.on_generate(child)

    logger.log("[Thất bại] Stack rỗng, không tìm được lời giải.")
    return logger.finalize(False)
