from algorithms.base import SearchLogger
from game.state import GameState


def causes_deadlock(child_state):
    if child_state.is_goal():
        return False
    return len(child_state.get_actions()) == 0


def forwardchecking_search(initial_state: GameState, max_steps=200000):
    logger = SearchLogger("Forward Checking")
    total = initial_state.board.num_remaining_tiles() // 2
    step_counter = [0]

    logger.log(f"[Forward Checking] Bắt đầu | {total} cặp cần gán", state=initial_state)

    def backtrack(state, assigned_order):
        step_counter[0] += 1
        if step_counter[0] > max_steps:
            return None

        logger.on_expand(state)

        if state.is_goal():
            return assigned_order

        candidates = state.get_actions()

        viable_candidates = []
        pruned_count = 0
        for candidate in candidates:
            child = state.apply_action(candidate)
            if causes_deadlock(child):
                pruned_count += 1
                continue
            viable_candidates.append((candidate, child))

        prev = assigned_order[-1] if assigned_order else None
        action_part = f"Nối:({prev[0]},{prev[1]})-({prev[2]},{prev[3]}) | " if prev else ""
        logger.log(
            f"[Mở rộng] {action_part}Depth:{len(assigned_order)}/{total} | FC Khả dĩ:{len(viable_candidates)} (Cắt:{pruned_count}) | Child:{len(candidates)}",
            state=state
        )

        for candidate, child in viable_candidates:
            logger.on_generate(child)
            r1, c1, r2, c2 = candidate

            result = backtrack(child, assigned_order + [candidate])
            if result is not None:
                return result

            logger.log(
                f"[Quay lui] Bỏ Nối:({r1},{c1})-({r2},{c2}) | Depth:{len(assigned_order)}",
                state=state
            )

        return None

    solution = backtrack(initial_state, [])

    if solution is not None:
        logger.log(f"[Xong] {len(solution)} cặp gán thành công!")
        return logger.finalize(True, actions=solution, states=[], cost=len(solution))
    else:
        logger.log("[Thất bại] Không tìm được thứ tự xóa hợp lệ.")
        return logger.finalize(False)