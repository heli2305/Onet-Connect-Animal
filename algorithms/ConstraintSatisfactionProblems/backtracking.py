from algorithms.base import SearchLogger
from game.state import GameState


def backtracking_search(initial_state: GameState, max_steps=200000):
    logger = SearchLogger("Backtracking (CSP)")
    total = initial_state.board.num_remaining_tiles() // 2
    step_counter = [0]

    logger.log(f"[CSP] Bắt đầu | {total} cặp cần gán", state=initial_state)

    def backtrack(state, assigned_order):
        step_counter[0] += 1
        if step_counter[0] > max_steps:
            return None

        logger.on_expand(state)

        if state.is_goal():
            return assigned_order

        candidates = state.get_actions()
        prev = assigned_order[-1] if assigned_order else None
        action_part = f"Nối:({prev[0]},{prev[1]})-({prev[2]},{prev[3]}) | " if prev else ""
        logger.log(
            f"[Mở rộng] {action_part}Depth:{len(assigned_order)}/{total} | Child:{len(candidates)}",
            state=state
        )

        for candidate in candidates:
            r1, c1, r2, c2 = candidate
            child = state.apply_action(candidate)
            logger.on_generate(child)

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