
import csv
from pathlib import Path

from src.environment.environment import (
    INITIAL_STATE,
    get_successors,
    get_state_time_minutes,
    is_goal
)

from src.visualization.visualization import (
    draw_park_map,
    draw_detailed_path,
    draw_action_timeline,
    draw_performance_comparison
)


ALGORITHMS = ["BFS", "DFS", "UCS", "IDS"]

METRIC_KEYS = [
    "path_cost",
    "trip_time",
    "nodes_generated",
    "nodes_expanded",
    "max_frontier_size",
    "execution_time"
]


def validate_path(path):
    if not isinstance(path, (list, tuple)) or not path:
        return False, "Path is empty", 0

    try:
        states = [tuple(state) for state in path]
    except (TypeError, ValueError):
        return False, "Invalid state format", 0

    if states[0] != INITIAL_STATE:
        return False, "Path must start at Entrance", 0

    total_cost = 0

    for i in range(1, len(states)):
        current = states[i - 1]
        next_state = states[i]

        transitions = get_successors(current)

        matching = [
            cost
            for successor, action, cost in transitions
            if successor == next_state
        ]

        if not matching:
            return False, f"Invalid transition at step {i}", 0

        total_cost += matching[0]

    return True, "Valid transitions", total_cost


def prepare_result(name, raw_result):
    if raw_result is None:
        raw_result = {}

    if not isinstance(raw_result, dict):
        raise ValueError(
            f"{name}: Result must be a dictionary"
        )

    path = raw_result.get("path") or []

    if path:
        valid, message, cost = validate_path(path)

        if not valid:
            raise ValueError(f"{name}: {message}")

        states = [tuple(state) for state in path]
        goal_reached = is_goal(states[-1])

        path_cost = cost
        trip_time = get_state_time_minutes(states[-1])

    else:
        states = []
        goal_reached = False
        path_cost = None
        trip_time = None

    if goal_reached:
        status = "SUCCESS"
    elif states:
        status = "INCOMPLETE"
    else:
        status = "NO_SOLUTION"

    result = {
        "algorithm": name,
        "status": status,
        "path": states,
        "path_cost": path_cost,
        "trip_time": trip_time,
        "nodes_generated": raw_result.get("nodes_generated"),
        "nodes_expanded": raw_result.get("nodes_expanded"),
        "max_frontier_size": raw_result.get("max_frontier_size"),
        "execution_time": raw_result.get("execution_time")
    }

    return result


def save_comparison_table(results):
    output_dir = Path("results/tables")
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = output_dir / "algorithm_comparison.csv"

    fields = [
        "algorithm",
        "status"
    ] + METRIC_KEYS

    with open(
        filename,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fields
        )

        writer.writeheader()

        for name, result in results.items():
            row = {
                key: result.get(key)
                for key in fields
            }

            writer.writerow(row)

    print("Saved:", filename)


def process_algorithm_results(
    algorithm_results,
    show=False
):
    if not isinstance(algorithm_results, dict):
        raise ValueError(
            "Algorithm results must be a dictionary"
        )

    processed = {}
    successful = {}

    print("\nALGORITHM INTEGRATION")
    print("---------------------")

    for name in ALGORITHMS:
        if name not in algorithm_results:
            print(f"{name}: Not available")
            continue

        raw_result = algorithm_results[name]

        result = prepare_result(
            name,
            raw_result
        )

        processed[name] = result

        print(f"\n{name}")
        print("Status:", result["status"])
        print("Path cost:", result["path_cost"])
        print("Trip time:", result["trip_time"])

        if result["status"] == "SUCCESS":
            successful[name] = result

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

    save_comparison_table(processed)

    if successful:
        draw_performance_comparison(
            successful,
            show=show
        )

        print("\nPerformance graphs generated.")
    else:
        print("\nNo successful solutions to compare.")

    return processed


def generate_environment_map():
    draw_park_map(show=False)
    print("Environment map generated.")


if __name__ == "__main__":
    generate_environment_map()

    print("\nIntegration module ready.")
    print("Waiting for algorithm results.")
