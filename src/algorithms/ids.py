import time

from src.environment import INITIAL_STATE, is_goal, get_successors



def ids(initial_state=INITIAL_STATE, max_depth=100):
    started = time.perf_counter()
    metrics = {"nodes_generated": 1, "nodes_expanded": 0, "max_frontier_size": 1}
    discovered = {initial_state}

    for depth_limit in range(max_depth + 1):
        iteration = {"new_state": False, "cutoff": False}
        shallowest_depth = {initial_state: 0}
        path_states = {initial_state}
        path = [initial_state]
        actions = []

        found = _depth_limited_search(
            initial_state, depth_limit, path_states, path, actions,
            shallowest_depth, discovered, iteration, metrics,
        )
        if found:
            elapsed = time.perf_counter() - started
            return {
                "algorithm": "IDS",
                "path": list(path),
                "actions": [action for action, _step_cost in actions],
                "path_cost": found,
                "estimated_trip_time_minutes": found * 15,
                **metrics,
                "depth_limit": depth_limit,
                "execution_time": elapsed,
            }
        if not iteration["new_state"] and not iteration["cutoff"]:
            break

    return {
        "algorithm": "IDS", "path": None, "actions": None,
        "path_cost": None, "estimated_trip_time_minutes": None,
        **metrics,
        "execution_time": time.perf_counter() - started,
    }


def _depth_limited_search(
    state, remaining_depth, path_states, path, actions,
    shallowest_depth, discovered, iteration, metrics,
):
    if is_goal(state):
        return sum(step_cost for _action, step_cost in actions)
    if remaining_depth == 0:
        iteration["cutoff"] = True
        return None

    metrics["nodes_expanded"] += 1
    current_depth = len(path) - 1
    for next_state, action, step_cost in get_successors(state):
        if next_state in path_states:
            continue
        next_depth = current_depth + 1
        if shallowest_depth.get(next_state, float("inf")) <= next_depth:
            continue

        shallowest_depth[next_state] = next_depth
        if next_state not in discovered:
            discovered.add(next_state)
            metrics["nodes_generated"] += 1
            iteration["new_state"] = True

        path_states.add(next_state)
        path.append(next_state)
        actions.append((action, step_cost))
        metrics["max_frontier_size"] = max(
            metrics["max_frontier_size"], len(path)
        )

        result = _depth_limited_search(
            next_state, remaining_depth - 1, path_states, path, actions,
            shallowest_depth, discovered, iteration, metrics,
        )
        if result is not None:
            return result

        actions.pop()
        path.pop()
        path_states.remove(next_state)
    return None


def iterative_deepening_search(initial_state=INITIAL_STATE, max_depth=100):
    return ids(initial_state, max_depth)


def print_result(result):
    print("Iterative Deepening Search (IDS)")
    if not result["path"]:
        print("No valid route exists in the reachable state space.")
    else:
        for index, state in enumerate(result["path"]):
            if index == 0:
                print(f"Start: {state}")
            else:
                action = result["actions"][index - 1]
                print(f"  {action[0]} {action[1]} -> {state}")
        print(f"Found at depth limit: {result['depth_limit']}")
        print(f"Path cost: {result['path_cost']} units")
        print(f"Estimated trip time: {result['estimated_trip_time_minutes']} minutes")
    print(f"Nodes generated: {result['nodes_generated']}")
    print(f"Nodes expanded: {result['nodes_expanded']}")
    print(f"Maximum active path size: {result['max_frontier_size']}")
    print(f"Running time: {result['execution_time']:.6f} seconds")


if __name__ == "__main__":
    print_result(ids())