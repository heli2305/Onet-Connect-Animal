from algorithms.base import SearchLogger


MAX_NODES = 50000


def get_possible_outcomes(state, action):
    outcomes = [state.apply_action(action)]
    for other in state.get_actions():
        if other != action:
            outcomes.append(state.apply_action(other))
            break
    return outcomes


def or_search(state, path, logger, node_counter):
    if state.is_goal():
        return {"type": "goal"}

    if state.key() in path:
        return None

    if node_counter[0] >= MAX_NODES:
        return None

    node_counter[0] += 1
    new_path = path | {state.key()}
    logger.on_expand(state)

    actions = state.get_actions()
    if not actions:
        return None

    first = actions[0]
    r1, c1, r2, c2 = first
    outcomes = get_possible_outcomes(state, first)

    if len(outcomes) >= 2:
        logger.log(
            f"[OR] ({r1},{c1})-({r2},{c2}) -> AND | outcome đúng + nhiễu",
            state=state.board
        )
        sub_plans = and_search(first, outcomes, new_path, logger, node_counter)
        if sub_plans is not None:
            return {"type": "and", "action": first, "sub_plans": sub_plans}
    else:
        sub_plan = or_search(outcomes[0], new_path, logger, node_counter)
        if sub_plan is not None:
            return {"type": "or", "action": first, "sub_plan": sub_plan}

    # Các action còn lại: thử tất định, không log từng bước
    for action in actions[1:]:
        child = state.apply_action(action)
        logger.on_generate(child)
        sub_plan = or_search(child, new_path, logger, node_counter)
        if sub_plan is not None:
            return {"type": "or", "action": action, "sub_plan": sub_plan}

    return None


def and_search(action, outcomes, path, logger, node_counter):
    plans = []
    r1, c1, r2, c2 = action
    for i, outcome in enumerate(outcomes):
        label = "đúng ý" if i == 0 else "nhiễu"
        logger.log(
            f"[AND] outcome {label} | ({r1},{c1})-({r2},{c2})",
            state=outcome.board
        )
        logger.on_generate(outcome)
        plan = or_search(outcome, path, logger, node_counter)
        if plan is None:
            return None
        plans.append(plan)
    return plans


def flatten_plan(plan):
    if plan is None or plan["type"] == "goal":
        return []
    if plan["type"] == "or":
        return [plan["action"]] + flatten_plan(plan["sub_plan"])
    if plan["type"] == "and":
        result = [plan["action"]]
        for sp in plan["sub_plans"]:
            result += flatten_plan(sp)
        return result
    return []


def and_or_search(initial_state):
    logger = SearchLogger("AND-OR Graph Search")
    total = initial_state.board.num_remaining_tiles() // 2
    logger.log(
        f"[AND-OR] Bắt đầu | {total} cặp | "
        f"Mô hình: action đầu tiên mỗi bước có thể nhiễu sang cặp khác",
        state=initial_state.board
    )

    node_counter = [0]
    plan = or_search(initial_state, set(), logger, node_counter)

    if plan is None:
        logger.log(f"[Thất bại] Không tìm được plan. Nodes={node_counter[0]}")
        return logger.finalize(False)

    actions = flatten_plan(plan)
    logger.log(f"[Xong] Plan: {len(actions)} bước | Nodes={node_counter[0]}")
    return logger.finalize(True, actions=actions, cost=len(actions))