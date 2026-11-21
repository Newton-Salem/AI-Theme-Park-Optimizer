import heapq
import itertools
import time

try:
    from src.environment.environment import INITIAL_STATE, get_successors, is_goal
except ModuleNotFoundError:
    from park_model import INITIAL_STATE, get_successors, is_goal


def ucs(initial_state=INITIAL_STATE):
    started = time.perf_counter()
    sequence = itertools.count()
    frontier = [(0, next(sequence), initial_state)]
    best_cost = {initial_state: 0}
    parent = {initial_state: None}
    nodes_generated = 1
    nodes_expanded = 0
    max_frontier_size = 1

    while frontier:
        cost, _, state = heapq.heappop(frontier)
        if cost != best_cost.get(state):
            continue
        if is_goal(state):
            return _build_result(
                state, parent, cost, nodes_generated, nodes_expanded,
                max_frontier_size, time.perf_counter() - started,
            )

        nodes_expanded += 1
        for next_state, action, step_cost in get_successors(state):
            new_cost = cost + step_cost
            if new_cost < best_cost.get(next_state, float("inf")):
                is_new_state = next_state not in best_cost
                best_cost[next_state] = new_cost
                parent[next_state] = (state, action, step_cost)
                heapq.heappush(frontier, (new_cost, next(sequence), next_state))
                if is_new_state:
                    nodes_generated += 1
        max_frontier_size = max(max_frontier_size, len(frontier))

    return _no_solution(nodes_generated, nodes_expanded, max_frontier_size,
                        time.perf_counter() - started)


def _build_result(goal, parent, cost, generated, expanded, max_frontier, elapsed):
    path = []
    actions = []
    state = goal
    while state is not None:
        path.append(state)
        link = parent[state]
        if link is None:
            break
        previous, action, _step_cost = link
        actions.append(action)
        state = previous
    path.reverse()
    actions.reverse()
    return {
        "algorithm": "UCS",
        "path": path,
        "actions": actions,
        "path_cost": cost,
        "estimated_trip_time_minutes": cost * 15,
        "nodes_generated": generated,
        "nodes_expanded": expanded,
        "max_frontier_size": max_frontier,
        "execution_time": elapsed,
    }


def _no_solution(generated, expanded, max_frontier, elapsed):
    return {
        "algorithm": "UCS", "path": None, "actions": None,
        "path_cost": None, "estimated_trip_time_minutes": None,
        "nodes_generated": generated, "nodes_expanded": expanded,
        "max_frontier_size": max_frontier, "execution_time": elapsed,
    }


def uniform_cost_search(initial_state=INITIAL_STATE):
    return ucs(initial_state)


def print_result(result):
    print("Uniform Cost Search (UCS)")
    if not result["path"]:
        print("No valid route exists within the time budget.")
    else:
        for index, state in enumerate(result["path"]):
            if index == 0:
                print(f"Start: {state}")
            else:
                action = result["actions"][index - 1]
                print(f"  {action[0]} {action[1]} -> {state}")
        print(f"Path cost: {result['path_cost']} units")
        print(f"Estimated trip time: {result['estimated_trip_time_minutes']} minutes")
    print(f"Nodes generated: {result['nodes_generated']}")
    print(f"Nodes expanded: {result['nodes_expanded']}")
    print(f"Maximum frontier size: {result['max_frontier_size']}")
    print(f"Running time: {result['execution_time']:.6f} seconds")


if __name__ == "__main__":
    print_result(ucs())