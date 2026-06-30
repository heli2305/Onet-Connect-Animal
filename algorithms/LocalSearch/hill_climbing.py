from algorithms.base import SearchLogger
from game.state import GameState


def hill_climbing_search(initial_state: GameState):
    logger = SearchLogger("Hill Climbing")
    total_pairs = initial_state.board.num_remaining_tiles() // 2
    logger.log(f"[Hill Climbing] Bắt đầu | Cặp cần gán: {total_pairs}", state=initial_state)

    if initial_state.is_goal():
        logger.log("[Xong] Bàn cờ đã trống ngay từ đầu.")
        return logger.finalize(True, [], [], cost=0)

    current_state = initial_state
    actions_taken = []
    states_visited = [initial_state]

    step = 0
    while not current_state.is_goal():
        logger.on_expand(current_state)
        
        actions = current_state.get_actions()
        if not actions:
            logger.log(f"[Thất bại] Bị kẹt tại bước {step}. Không có nước đi khả dĩ (Local Optimum).", state=current_state)
            return logger.finalize(False, actions_taken, states_visited, len(actions_taken))

        prev = actions_taken[-1] if actions_taken else None
        action_part = f"Nối:({prev[0]},{prev[1]})-({prev[2]},{prev[3]}) | " if prev else ""
        logger.log(
            f"[Mở rộng] {action_part}Mật độ láng giềng:{len(actions)} | Child:{len(actions)}",
            state=current_state
        )

        best_action = None
        best_value = -1
        best_child = None

        for action in actions:
            child = current_state.apply_action(action)
            logger.on_generate(child)
            
            if child.is_goal():
                val = 999999
            else:
                val = len(child.get_actions())

            if val > best_value:
                best_value = val
                best_action = action
                best_child = child

        r1, c1, r2, c2 = best_action
        logger.log(
            f"[Gán] Nối:({r1},{c1})-({r2},{c2}) | Láng giềng tốt nhất có {best_value if best_value != 999999 else 0} nước tiếp theo",
            state=best_child
        )

        current_state = best_child
        actions_taken.append(best_action)
        states_visited.append(current_state)
        step += 1

    logger.log(f"[Xong] Giải thành công sau {step} cặp!", state=current_state)
    return logger.finalize(True, actions_taken, states_visited, len(actions_taken))
