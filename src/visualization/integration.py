
"""Connect BFS, DFS, UCS and IDS to visualization."""

from src.environment.environment import (
    INITIAL_STATE,
    get_successors,
    get_state_time_minutes,
    is_goal,
    TIME_UNIT_MINUTES
)

from src.visualization.visualization import (
    draw_park_map,
    draw_detailed_path,
    draw_action_timeline,
    draw_performance_comparison,
    save_results_table
)


ALGORITHMS = ("BFS", "DFS", "UCS", "IDS")

METRIC_KEYS = (
    "nodes_generated",
    "nodes_expanded",
    "max_frontier_size",
    "execution_time"
)


def validate_path(path):
    """Validate a path and calculate its total cost."""

    if not isinstance(path, (list, tuple)) or not path:
        return False, "Empty path", 0

    try:
        states = [tuple(state) for state in path]
    except (TypeError, ValueError):
        return False, "Invalid state format", 0

    if any(len(state) != 3 for state in states):
        return False, "Each state must have three elements", 0

    if states[0] != INITIAL_STATE:
        return False, "Path does not start at Entrance", 0

    total_cost = 0

    for step, (previous, nxt) in enumerate(
        zip(states, states[1:]), start=1
    ):
        matching = [
            cost
            for state, action, cost in get_successors(previous)
            if state == nxt
        ]

        if not matching:
            return (
                False,
                f"Invalid transition at step {step}",
                0
            )

        total_cost += matching[0]

    return True, "All transitions are valid", total_cost


def prepare_result(name, raw_result):
    """Normalize results from the team's algorithms."""

    name = name.upper()

    if not isinstance(raw_result, dict):
        raise ValueError(
            f"{name}: Expected a dictionary result"
        )

    declared_name = raw_result.get("algorithm")

    if declared_name:
        if str(declared_name).upper() != name:
            raise ValueError(
                f"{name}: Algorithm name mismatch"
            )

    path = raw_result.get("path")

    if path is None or path == []:
        if raw_result.get("actions") not in (None, []):
            raise ValueError(
                f"{name}: Actions supplied without a path"
            )

        if raw_result.get("path_cost") is not None:
            raise ValueError(
                f"{name}: Cost supplied without a path"
            )

        states = []
        status = "NO_SOLUTION"
        cost = None
        minutes = None
        actions = []

    else:
        valid, message, cost = validate_path(path)

        if not valid:
            raise ValueError(f"{name}: {message}")

        states = [tuple(state) for state in path]
        actions = []

        for previous, nxt in zip(
            states, states[1:]
        ):
            matches = [
                action
                for state, action, step_cost
                in get_successors(previous)
                if state == nxt
            ]

            actions.append(matches[0])

        provided_actions = raw_result.get("actions")

        if provided_actions is not None:
            if list(provided_actions) != actions:
                raise ValueError(
                    f"{name}: Actions do not match path"
                )

        provided_cost = raw_result.get("path_cost")

        if provided_cost is not None:
            if provided_cost != cost:
                raise ValueError(
                    f"{name}: Incorrect path cost"
                )

        minutes = get_state_time_minutes(
            states[-1]
        )

        provided_minutes = raw_result.get(
            "estimated_trip_time_minutes"
        )

        if provided_minutes is not None:
            if provided_minutes != minutes:
                raise ValueError(
                    f"{name}: Incorrect trip time"
                )

        status = (
            "SUCCESS"
            if is_goal(states[-1])
            else "INCOMPLETE"
        )

    normalized = {
        "algorithm": name,
        "status": status,
        "path": states,
        "actions": actions,
        "path_cost": cost,
        "estimated_trip_time_minutes": minutes
    }

    for key in METRIC_KEYS:
        value = raw_result.get(key)

        if value is not None:
            if (
                not isinstance(value, (int, float))
                or value < 0
            ):
                raise ValueError(
                    f"{name}: Invalid metric {key}"
                )

        normalized[key] = value

    if "depth_limit" in raw_result:
        normalized["depth_limit"] = (
            raw_result["depth_limit"]
        )

    return normalized


def save_comparison_table(results):
    return save_results_table(results)


def process_algorithm_results(
    algorithm_results,
    show=False,
    draw_map=True
):
    if not isinstance(algorithm_results, dict):
        raise ValueError(
            "Algorithm results must be a dictionary"
        )

    if draw_map:
        draw_park_map(show=show)

    processed = {}

    print("\nALGORITHM RESULTS")
    print("-" * 55)

    for name in ALGORITHMS:
        raw = algorithm_results.get(name)

        if raw is None:
            print(f"{name}: NOT PROVIDED")
            continue

        result = prepare_result(name, raw)
        processed[name] = result

        print(
            f"{name}: {result['status']} | "
            f"Cost={result['path_cost']} | "
            f"Time={result['estimated_trip_time_minutes']} | "
            f"Expanded={result['nodes_expanded']} | "
            f"Runtime={result['execution_time']}"
        )

        if result["path"]:
            draw_detailed_path(
                result["path"],
                algorithm=name,
                show=show
            )

            draw_action_timeline(
                result["path"],
                algorithm=name,
                show=show
            )

    if processed:
        save_comparison_table(processed)

        draw_performance_comparison(
            processed,
            show=show
        )

    return processed


def generate_environment_map():
    draw_park_map(show=False)


def run_all_algorithms(show=False):
    from src.algorithms.bfs import bfs
    from src.algorithms.dfs import dfs
    from src.algorithms.ucs import ucs
    from src.algorithms.ids import ids

    raw_results = {
        "BFS": bfs(),
        "DFS": dfs(),
        "UCS": ucs(),
        "IDS": ids()
    }

    return process_algorithm_results(
        raw_results,
        show=show
    )


if __name__ == "__main__":
    run_all_algorithms(show=False)
