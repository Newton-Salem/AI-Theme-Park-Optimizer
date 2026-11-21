
import time
from collections import deque
from src.environment.environment import INITIAL_STATE, is_goal, get_successors


def bfs():
    start_time = time.perf_counter()

    queue = deque([INITIAL_STATE])
    visited = {INITIAL_STATE}
    parent = {INITIAL_STATE: None}

    nodes_generated = 1
    nodes_expanded = 0
    max_frontier_size = 1

    while queue:
        current_state = queue.popleft()

        if is_goal(current_state):
            path = []
            actions = []
            path_cost = 0
            state = current_state

            while state is not None:
                path.append(state)
                parent_info = parent[state]

                if parent_info is None:
                    break

                previous_state, action, step_cost = parent_info
                actions.append(action)
                path_cost += step_cost
                state = previous_state

            path.reverse()
            actions.reverse()

            execution_time = time.perf_counter() - start_time

            return {
                "algorithm": "BFS",
                "path": path,
                "actions": actions,
                "path_cost": path_cost,
                "estimated_trip_time_minutes": path_cost * 15,
                "nodes_generated": nodes_generated,
                "nodes_expanded": nodes_expanded,
                "max_frontier_size": max_frontier_size,
                "execution_time": execution_time
            }

        nodes_expanded += 1

        for next_state, action, step_cost in get_successors(current_state):
            if next_state not in visited:
                visited.add(next_state)
                parent[next_state] = (
                    current_state,
                    action,
                    step_cost
                )
                queue.append(next_state)
                nodes_generated += 1

        max_frontier_size = max(max_frontier_size, len(queue))

    execution_time = time.perf_counter() - start_time

    return {
        "algorithm": "BFS",
        "path": None,
        "actions": None,
        "path_cost": None,
        "estimated_trip_time_minutes": None,
        "nodes_generated": nodes_generated,
        "nodes_expanded": nodes_expanded,
        "max_frontier_size": max_frontier_size,
        "execution_time": execution_time
    }
