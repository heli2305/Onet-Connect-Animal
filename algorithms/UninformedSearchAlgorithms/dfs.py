from algorithms.base import SearchLogger, reconstruct_path, feedforward_heuristic


def dfs(initial_state):
    logger = SearchLogger("DFS (FF)")
    total_pairs = initial_state.board.num_remaining_tiles() // 2
    logger.log(f"[DFS] Bắt đầu | Frontier:1 | Cặp còn:{total_pairs}", state=initial_state)

    if initial_state.is_goal():
        return logger.finalize(True, [], [initial_state], 0)

    stack = [initial_state]
    visited = {initial_state}
    came_from = {initial_state: None}
    logger.on_generate(initial_state)

    while stack:
        state = stack.pop()
        logger.on_expand(state)

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

        children_with_h = []
        for action in actions:
            child = state.apply_action(action)
            if child not in visited:
                h_val = feedforward_heuristic(child)
                children_with_h.append((h_val, child, action))

        children_with_h.sort(key=lambda item: item[0], reverse=True)

        for h_val, child, action in children_with_h:
            visited.add(child)
            came_from[child] = (state, action)
            
            if child.is_goal():
                logger.log(f"[Xong] Tìm thấy sau {logger.expanded_nodes + 1} bước!")
                path_states, path_actions = reconstruct_path(came_from, child)
                return logger.finalize(True, path_actions, path_states, cost=len(path_actions))
            
            stack.append(child)
            logger.on_generate(child)

    logger.log("[Thất bại] Stack rỗng, không tìm được lời giải.")
    return logger.finalize(False)
