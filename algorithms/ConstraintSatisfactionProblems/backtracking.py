from algorithms.base import SearchLogger
from game.state import GameState


def backtracking_search(initial_state: GameState, max_steps=200000):
    logger = SearchLogger("Backtracking (CSP)")
    total = initial_state.board.num_remaining_tiles() // 2
    step_counter = [0]

    logger.log(f"[CSP] Bắt đầu | {total} cặp cần gán", state=initial_state.board)

    def backtrack(state, assigned_order):
        step_counter[0] += 1
        if step_counter[0] > max_steps:
            return None

        logger.on_expand()

        if state.is_goal():
            return assigned_order

        candidates = state.get_actions()

        for candidate in candidates:
            logger.on_generate()
            r1, c1, r2, c2 = candidate

            child = state.apply_action(candidate)

            logger.log(
                f"[Gán] ({r1},{c1})→({r2},{c2}) | Depth:{len(assigned_order)+1}/{total}",
                state=child.board
            )

            result = backtrack(child, assigned_order + [candidate])
            if result is not None:
                return result

            logger.log(
                f"[Quay lui] Bỏ ({r1},{c1})→({r2},{c2}) | Depth:{len(assigned_order)}",
                state=state.board
            )

        return None

    solution = backtrack(initial_state, [])

    if solution is not None:
        logger.log(f"[Xong] {len(solution)} cặp gán thành công!")
        return logger.finalize(True, actions=solution, states=[], cost=len(solution))
    else:
        logger.log("[Thất bại] Không tìm được thứ tự xóa hợp lệ.")
        return logger.finalize(False)