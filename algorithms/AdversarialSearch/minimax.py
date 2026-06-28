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


def minimax_search(initial_state: GameState, depth_limit=3):
    logger = SearchLogger("Minimax")
    best_action_holder = [None]

    def minimax(state, depth, player, last_action=None):
        logger.on_expand(state)
        
        player_name = "MAX" if player == MAX_PLAYER else "MIN"
        action_part = f"Nối:({last_action[0]},{last_action[1]})-({last_action[2]},{last_action[3]}) | " if last_action else ""
        actions = state.get_actions()
        
        logger.log(
            f"[Mở rộng Minimax] {player_name} (d={depth}) | {action_part}Child:{len(actions)}",
            state=state
        )

        if not actions or depth == 0:
            return evaluate_state(state, player)

        if player == MAX_PLAYER:
            value = float("-inf")
            for a in actions:
                logger.on_generate(state.apply_action(a))
                child_value = minimax(state.apply_action(a), depth - 1, MIN_PLAYER, a)
                if child_value > value:
                    value = child_value
                    if depth == depth_limit:
                        best_action_holder[0] = a
            return value
        else:
            value = float("inf")
            for a in actions:
                logger.on_generate(state.apply_action(a))
                child_value = minimax(state.apply_action(a), depth - 1, MAX_PLAYER, a)
                if child_value < value:
                    value = child_value
            return value

    logger.log(f"[Minimax] Bắt đầu | depth_limit={depth_limit}", state=initial_state)
    root_value = minimax(initial_state, depth_limit, MAX_PLAYER)
    logger.log(f"[Xong] Giá trị={root_value} | Nước đề xuất={best_action_holder[0]}")
    if best_action_holder[0] is not None:
        return logger.finalize(True, actions=[best_action_holder[0]], cost=root_value)
    return logger.finalize(False)


def minimax_search_full(initial_state: GameState, depth_limit=3):
    logger = SearchLogger("Minimax (Adversarial)")
    current_state = initial_state
    actions_taken = []
    logger.log(f"[Minimax] Bắt đầu | {initial_state.board.num_remaining_tiles() // 2} cặp", state=initial_state.board)
    while not current_state.is_goal():
        res = minimax_search(current_state, depth_limit=depth_limit)
        logger.expanded_nodes += res.expanded_nodes
        logger.generated_nodes += res.generated_nodes
        
        # Sao chép các thông tin log và bước duyệt của lượt tìm kiếm minimax này
        logger.log_messages.extend(res.log_messages)
        logger.search_steps.extend(res.search_steps)
        
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
