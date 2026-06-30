from algorithms.base import SearchLogger


MAX_NODES = 50000


def get_possible_outcomes(state, action):
    outcomes = [state.apply_action(action)]
    for other in state.get_actions():
        if other != action:
            outcomes.append(state.apply_action(other))
            break
    return outcomes


MAX_NONDETERMINISTIC_DEPTH = 6
MAX_CANDIDATES_FOR_CHECK = 3


def or_search(state, path, logger, node_counter, depth=0):
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

    should_check_noise = (
        depth < MAX_NONDETERMINISTIC_DEPTH
        and len(actions) <= MAX_CANDIDATES_FOR_CHECK
    )

    if should_check_noise:
        outcomes = get_possible_outcomes(state, first)
    else:
        outcomes = [state.apply_action(first)]

    if len(outcomes) >= 2:
        logger.log(
            f"[OR] ({r1},{c1})-({r2},{c2}) -> AND | outcome đúng + nhiễu | depth={depth}",
            state=state.board
        )
        sub_plans = and_search(first, outcomes, new_path, logger, node_counter, depth)
        if sub_plans is not None:
            return {"type": "and", "action": first, "sub_plans": sub_plans}
    else:
        sub_plan = or_search(outcomes[0], new_path, logger, node_counter, depth + 1)
        if sub_plan is not None:
            return {"type": "or", "action": first, "sub_plan": sub_plan}

    for action in actions[1:]:
        child = state.apply_action(action)
        logger.on_generate(child)
        sub_plan = or_search(child, new_path, logger, node_counter, depth + 1)
        if sub_plan is not None:
            return {"type": "or", "action": action, "sub_plan": sub_plan}

    return None


def and_search(action, outcomes, path, logger, node_counter, depth):
    plans = []
    r1, c1, r2, c2 = action
    for i, outcome in enumerate(outcomes):
        label = "đúng ý" if i == 0 else "nhiễu"
        logger.log(
            f"[AND] outcome {label} | ({r1},{c1})-({r2},{c2})",
            state=outcome.board
        )
        logger.on_generate(outcome)
        plan = or_search(outcome, path, logger, node_counter, depth + 1)
        if plan is None:
            return None
        plans.append(plan)
    return plans


def describe_plan(plan, indent=0):
    pad = "  " * indent
    if plan is None:
        return pad + "(thất bại)"
    if plan["type"] == "goal":
        return pad + "[Đạt mục tiêu]"
    if plan["type"] == "or":
        r1, c1, r2, c2 = plan["action"]
        return (f"{pad}Nối ({r1},{c1})-({r2},{c2})\n"
                + describe_plan(plan["sub_plan"], indent + 1))
    if plan["type"] == "and":
        r1, c1, r2, c2 = plan["action"]
        s = f"{pad}Nối ({r1},{c1})-({r2},{c2})\n"
        labels = ["NẾU đúng ý", "NẾU nhiễu"]
        for label, sp in zip(labels, plan["sub_plans"]):
            s += f"{pad}  {label}:\n" + describe_plan(sp, indent + 2) + "\n"
        return s
    return pad + "?"


def get_executable_actions(plan):
    actions = []
    node = plan
    while node is not None and node["type"] != "goal":
        actions.append(node["action"])
        if node["type"] == "or":
            node = node["sub_plan"]
        else:  
            node = node["sub_plans"][0]
    return actions


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

    logger.log("[Plan có điều kiện]")
    for line in describe_plan(plan).split("\n"):
        if line.strip():
            logger.log(line)

    actions = get_executable_actions(plan)
    logger.log(f"[Xong] Plan: {len(actions)} bước thực thi | Nodes={node_counter[0]}")
    return logger.finalize(True, actions=actions, cost=len(actions))