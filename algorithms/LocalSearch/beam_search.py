from algorithms.base import SearchLogger, reconstruct_path, feedforward_heuristic


def beam_search(initial_state, beam_width=5):
    logger = SearchLogger("Beam Search (FF)")
    came_from = {initial_state: None}
    
    logger.on_generate(initial_state)
    logger.log(f"[Beam Search] Bắt đầu | beam_width={beam_width} | Frontier:1", state=initial_state)

    if initial_state.is_goal():
        states, actions = reconstruct_path(came_from, initial_state)
        return logger.finalize(True, actions, states, cost=0)

    current_layer = [initial_state]
    visited = {initial_state}
    step = 0

    while current_layer:
        logger.log(f"--- Bước {step} | Size:{len(current_layer)} ---")
        next_candidates = []

        for state in current_layer:
            logger.on_expand(state)
            for action in state.get_actions():
                child = state.apply_action(action)
                if child not in visited:
                    visited.add(child)
                    came_from[child] = (state, action)
                    
                    if child.is_goal():
                        logger.log(f"[Xong] Tìm thấy lời giải!")
                        states, actions = reconstruct_path(came_from, child)
                        return logger.finalize(True, actions, states, cost=len(actions))
                    
                    h_val = feedforward_heuristic(child)
                    next_candidates.append((h_val, child))
                    logger.on_generate(child)

        next_candidates.sort(key=lambda item: item[0])
        current_layer = [state for _, state in next_candidates[:beam_width]]
        step += 1

    logger.log("[Thất bại] Không tìm được lời giải.")
    return logger.finalize(False)
