from algorithms.base import SearchLogger, reconstruct_path


def local_beam_search(initial_state, beam_width=5):
    logger = SearchLogger("Local beam search")
    came_from = {initial_state: None}
    
    logger.on_generate(initial_state)
    logger.log(f"[Local beam search] Bắt đầu | beam_width={beam_width} | Frontier:1", state=initial_state)

    if initial_state.is_goal():
        states, actions = reconstruct_path(came_from, initial_state)
        return logger.finalize(True, actions, states, cost=0)

    current_layer = [initial_state]
    visited = {initial_state}
    step = 0

    while current_layer:
        logger.log(f"--- Bước {step} | Size:{len(current_layer)} ---")
        
        # Kiểm tra đích khi mở rộng các trạng thái trong tầng hiện tại
        for state in current_layer:
            if state.is_goal():
                logger.log(f"[Xong] Tìm thấy lời giải!")
                states, actions = reconstruct_path(came_from, state)
                return logger.finalize(True, actions, states, cost=len(actions))

        next_candidates = []

        for state in current_layer:
            logger.on_expand(state)
            
            prev = came_from.get(state)
            if prev:
                _, (r1, c1, r2, c2) = prev
                action_part = f"Nối:({r1},{c1})-({r2},{c2}) | "
            else:
                action_part = ""
            
            actions = state.get_actions()
            logger.log(
                f"[Mở rộng] {action_part}h={state.heuristic()} | Child:{len(actions)}",
                state=state
            )
            
            for action in actions:
                child = state.apply_action(action)
                if child not in visited:
                    visited.add(child)
                    came_from[child] = (state, action)
                    h_val = child.heuristic()
                    next_candidates.append((h_val, child))
                    logger.on_generate(child)

        next_candidates.sort(key=lambda item: item[0])
        current_layer = [state for _, state in next_candidates[:beam_width]]
        step += 1

    logger.log("[Thất bại] Không tìm được lời giải.")
    return logger.finalize(False)
