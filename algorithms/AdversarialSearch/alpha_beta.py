from algorithms.base import SearchLogger
from game.state import GameState

MAX_PLAYER = 1
MIN_PLAYER = -1


def evaluate_state(state, player):
    if state.is_goal():
        return 9999 if player == MAX_PLAYER else -9999
    available = len(state.get_actions())
    if available == 0:
        return -9999 if player == MAX_PLAYER else 9999
    return available if player == MAX_PLAYER else -available


def alpha_beta_search(initial_state: GameState, depth_limit=3):
    logger = SearchLogger("Alpha-Beta")
    best_action_holder = [None]

    def alphabeta(state, depth, player, alpha, beta):
        logger.on_expand()
        actions = state.get_actions()
        if not actions or depth == 0:
            return evaluate_state(state, player)
        if player == MAX_PLAYER:
            value = float("-inf")
            for a in actions:
                logger.on_generate()
                child_value = alphabeta(state.apply_action(a), depth - 1, MIN_PLAYER, alpha, beta)
                if child_value > value:
                    value = child_value
                    if depth == depth_limit:
                        best_action_holder[0] = a
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return value
        else:
            value = float("inf")
            for a in actions:
                logger.on_generate()
                child_value = alphabeta(state.apply_action(a), depth - 1, MAX_PLAYER, alpha, beta)
                if child_value < value:
                    value = child_value
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return value

    logger.log(f"[Alpha-Beta] Bắt đầu | depth_limit={depth_limit}", state=initial_state.board)
    root_value = alphabeta(initial_state, depth_limit, MAX_PLAYER, float("-inf"), float("inf"))
    logger.log(f"[Xong] Giá trị={root_value} | Nước đề xuất={best_action_holder[0]}")
    if best_action_holder[0] is not None:
        return logger.finalize(True, actions=[best_action_holder[0]], cost=root_value)
    return logger.finalize(False)


def alpha_beta_search_full(initial_state: GameState, depth_limit=3):
    logger = SearchLogger("Alpha-Beta (Adversarial)")
    current_state = initial_state
    actions_taken = []
    logger.log(f"[Alpha-Beta] Bắt đầu | {initial_state.board.num_remaining_tiles() // 2} cặp", state=initial_state.board)
    while not current_state.is_goal():
        res = alpha_beta_search(current_state, depth_limit=depth_limit)
        logger.expanded_nodes += res.expanded_nodes
        logger.generated_nodes += res.generated_nodes
        if not res.success or not res.actions:
            logger.log("[Thất bại] Bị kẹt.", state=current_state.board)
            return logger.finalize(False, actions_taken, [], len(actions_taken))
        action = res.actions[0]
        current_state = current_state.apply_action(action)
        actions_taken.append(action)
        r1, c1, r2, c2 = action
        logger.log(f"[Gán] ({r1},{c1})-({r2},{c2})", state=current_state.board)
    logger.log(f"[Xong] {len(actions_taken)} cặp!")
    return logger.finalize(True, actions_taken, [], len(actions_taken))
