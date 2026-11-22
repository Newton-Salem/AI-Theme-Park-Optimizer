# Metrics used to evaluate and compare search algorithms.

METRIC_KEYS = [
    "path_cost",
    "estimated_trip_time_minutes",
    "nodes_generated",
    "nodes_expanded",
    "max_frontier_size",
    "execution_time"
]


def validate_result(result):
    """
    Check whether an algorithm result contains all required metrics.
    """

    required_keys = ["algorithm", "path", "actions"] + METRIC_KEYS

    for key in required_keys:
        if key not in result:
            raise ValueError(
                f"Missing required key '{key}' in algorithm result."
            )

    return True


def extract_metrics(result):
    """
    Extract and organize metrics from one algorithm result.
    """

    validate_result(result)

    return {
        "algorithm": result["algorithm"],
        "solution_found": result["path"] is not None,
        "path_cost": result["path_cost"],
        "estimated_trip_time_minutes":
            result["estimated_trip_time_minutes"],
        "nodes_generated": result["nodes_generated"],
        "nodes_expanded": result["nodes_expanded"],
        "max_frontier_size": result["max_frontier_size"],
        "execution_time": result["execution_time"]
    }


def collect_metrics(results):
    """
    Collect metrics from multiple algorithm results.
    """

    metrics = []

    for result in results:
        metrics.append(extract_metrics(result))

    return metrics


def print_metrics_comparison(results):
    """
    Print a comparison of the search algorithms.
    """

    metrics = collect_metrics(results)

    headers = [
        "Algorithm",
        "Solution",
        "Path Cost",
        "Trip Time",
        "Generated",
        "Expanded",
        "Max Frontier",
        "Execution Time"
    ]

    print("\n" + "=" * 115)
    print("SEARCH ALGORITHMS PERFORMANCE COMPARISON")
    print("=" * 115)

    print(
        f"{headers[0]:<12}"
        f"{headers[1]:<12}"
        f"{headers[2]:<12}"
        f"{headers[3]:<12}"
        f"{headers[4]:<12}"
        f"{headers[5]:<12}"
        f"{headers[6]:<16}"
        f"{headers[7]:<15}"
    )

    print("-" * 115)

    for item in metrics:
        print(
            f"{item['algorithm']:<12}"
            f"{str(item['solution_found']):<12}"
            f"{str(item['path_cost']):<12}"
            f"{str(item['estimated_trip_time_minutes']):<12}"
            f"{item['nodes_generated']:<12}"
            f"{item['nodes_expanded']:<12}"
            f"{item['max_frontier_size']:<16}"
            f"{item['execution_time']:.6f}s"
        )

    print("=" * 115)

    return metrics