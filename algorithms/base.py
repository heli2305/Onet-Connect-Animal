import time
from dataclasses import dataclass, field


@dataclass
class SearchResult:

    success: bool                     
    actions: list = field(default_factory=list)
    states: list = field(default_factory=list)
    cost: int = 0
    expanded_nodes: int = 0
    generated_nodes: int = 0
    time_seconds: float = 0.0
    algorithm_name: str = ""
    log_messages: list = field(default_factory=list)
    search_steps: list = field(default_factory=list)


class SearchLogger:

    def __init__(self, algorithm_name: str):
        self.algorithm_name = algorithm_name
        self._start_time = time.perf_counter()
        self.expanded_nodes = 0
        self.generated_nodes = 0
        self.log_messages = []
        self.search_steps = []

    def on_expand(self, state=None):
        self.expanded_nodes += 1

    def on_generate(self, state=None):
        self.generated_nodes += 1

    def log(self, message: str, state=None):
        self.log_messages.append(message)
        snapshot = None
        if state is not None:
            if hasattr(state, "board") and hasattr(state.board, "clone"):
                snapshot = state.board.clone()
            elif hasattr(state, "clone"):
                snapshot = state.clone()
        self.search_steps.append((snapshot, message))

    def finalize(self, success, actions=None, states=None, cost=0) -> SearchResult:
        elapsed = time.perf_counter() - self._start_time
        return SearchResult(
            success=success,
            actions=actions or [],
            states=states or [],
            cost=cost,
            expanded_nodes=self.expanded_nodes,
            generated_nodes=self.generated_nodes,
            time_seconds=elapsed,
            algorithm_name=self.algorithm_name,
            log_messages=self.log_messages,
            search_steps=self.search_steps,
        )


def reconstruct_path(came_from, last_state):
    states = [last_state]
    actions = []
    cur = last_state
    while came_from.get(cur) is not None:
        parent, action = came_from[cur]
        states.append(parent)
        actions.append(action)
        cur = parent
    states.reverse()
    actions.reverse()
    return states, actions


