from algorithms.base import SearchLogger
from algorithms.ConstraintSatisfactionProblems.csp_problem import CSP
from game.board import Board


def backtracking_search(board: Board, max_steps=200000):
    logger = SearchLogger("Backtracking (CSP)")
    csp = CSP(board)
    remaining_variables = list(csp.variables)
    total = len(remaining_variables)

    logger.log(f"[CSP] Bắt đầu | {total} cặp cần gán", state=board)

    step_counter = [0]

    def backtrack(assigned_order, unassigned):
        step_counter[0] += 1
        if step_counter[0] > max_steps:
            return None

        logger.on_expand()

        if csp.is_complete(assigned_order):
            return assigned_order

        depth = len(assigned_order) + 1
        for i, candidate in enumerate(unassigned):
            logger.on_generate()
            r1, c1, r2, c2 = candidate
            if csp.is_consistent(assigned_order, candidate):
                assigned_board = board.clone()
                for (ar1, ac1, ar2, ac2) in assigned_order + [candidate]:
                    assigned_board.remove(ar1, ac1, ar2, ac2)

                logger.log(
                    f"[Gán] ({r1},{c1})→({r2},{c2}) | Depth:{depth}/{total} | Remain:{len(unassigned)-1}",
                    state=assigned_board
                )

                result = backtrack(assigned_order + [candidate], unassigned[:i] + unassigned[i + 1:])
                if result is not None:
                    return result

                backtrack_board = board.clone()
                for (ar1, ac1, ar2, ac2) in assigned_order:
                    backtrack_board.remove(ar1, ac1, ar2, ac2)

                logger.log(
                    f"[Quay lui] Bỏ ({r1},{c1})→({r2},{c2}) | Thử:{i+1} nhánh | Depth:{depth-1}",
                    state=backtrack_board
                )

        return None

    solution = backtrack([], remaining_variables)

    if solution is not None:
        logger.log(f"[Xong] {len(solution)} cặp gán thành công!")
        return logger.finalize(True, actions=solution, states=[], cost=len(solution))
    else:
        logger.log("[Thất bại] Không tìm được thứ tự xóa hợp lệ.")
        return logger.finalize(False)
