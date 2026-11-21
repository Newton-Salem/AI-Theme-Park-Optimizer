
from pathlib import Path
import csv

import matplotlib.pyplot as plt
import networkx as nx

from src.environment.environment import (
    LOCATIONS,
    PARK_EDGES,
    REQUIRED_ATTRACTIONS,
    INITIAL_STATE,
    TIME_UNIT_MINUTES,
)


OUTPUT_DIR = Path("results/graphs")
TABLE_DIR = Path("results/tables")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
TABLE_DIR.mkdir(parents=True, exist_ok=True)

COLORS = {
    "BFS": "#3498db",
    "DFS": "#e67e22",
    "UCS": "#27ae60",
    "IDS": "#9b59b6",
}


def create_graph():
    graph = nx.Graph()

    graph.add_nodes_from(LOCATIONS)

    for start, end, travel_time in PARK_EDGES:
        graph.add_edge(
            start,
            end,
            weight=travel_time
        )

    return graph


def get_positions():
    graph = create_graph()
    return nx.spring_layout(graph, seed=42)


def draw_park_map(save=True, show=True):
    graph = create_graph()
    pos = get_positions()

    plt.figure(figsize=(14, 9))

    node_colors = []

    for node in graph.nodes():
        if node == "Entrance":
            node_colors.append("#2ecc71")
        elif node == "Exit":
            node_colors.append("#e74c3c")
        elif node in REQUIRED_ATTRACTIONS:
            node_colors.append("#3498db")
        else:
            node_colors.append("#f1c40f")

    nx.draw_networkx(
        graph,
        pos,
        node_color=node_colors,
        node_size=2300,
        font_size=9,
        font_weight="bold",
        edge_color="#aaaaaa",
        width=2
    )

    edge_labels = nx.get_edge_attributes(graph, "weight")

    nx.draw_networkx_edge_labels(
        graph,
        pos,
        edge_labels=edge_labels,
        font_size=9
    )

    plt.title(
        "AI Theme Park - Environment Map",
        fontsize=18,
        fontweight="bold"
    )

    plt.axis("off")
    plt.tight_layout()

    if save:
        plt.savefig(
            OUTPUT_DIR / "theme_park_map.png",
            dpi=300,
            bbox_inches="tight"
        )

    if show:
        plt.show()

    plt.close()


def extract_locations(path):
    locations = []

    for item in path:
        if isinstance(item, str):
            location = item
        elif isinstance(item, (tuple, list)) and len(item) == 3:
            location = item[0]
        else:
            raise ValueError(
                "Path must contain location names or environment states"
            )

        if location not in LOCATIONS:
            raise ValueError(f"Unknown location: {location}")

        locations.append(location)

    return locations


def draw_solution_path(path, algorithm="BFS", save=True, show=True):
    graph = create_graph()
    pos = get_positions()

    locations = extract_locations(path)

    if not locations:
        raise ValueError("The solution path cannot be empty")

    path_edges = []

    for i in range(len(locations) - 1):
        start = locations[i]
        end = locations[i + 1]

        if start == end:
            continue

        if not graph.has_edge(start, end):
            raise ValueError(
                f"Invalid movement: {start} -> {end}"
            )

        path_edges.append((start, end))

    plt.figure(figsize=(14, 9))

    nx.draw_networkx(
        graph,
        pos,
        node_color="#dfe6e9",
        node_size=2200,
        font_size=9,
        edge_color="#d0d0d0",
        width=1.5
    )

    color = COLORS.get(algorithm.upper(), "#e74c3c")

    nx.draw_networkx_edges(
        graph,
        pos,
        edgelist=path_edges,
        edge_color=color,
        width=4
    )

    visited_nodes = list(dict.fromkeys(locations))

    nx.draw_networkx_nodes(
        graph,
        pos,
        nodelist=visited_nodes,
        node_color=color,
        node_size=2200
    )

    nx.draw_networkx_labels(
        graph,
        pos,
        font_size=9,
        font_weight="bold"
    )

    edge_labels = nx.get_edge_attributes(graph, "weight")

    nx.draw_networkx_edge_labels(
        graph,
        pos,
        edge_labels=edge_labels,
        font_size=8
    )

    plt.title(
        f"{algorithm.upper()} - Solution Path",
        fontsize=18,
        fontweight="bold"
    )

    plt.axis("off")
    plt.tight_layout()

    if save:
        plt.savefig(
            OUTPUT_DIR / f"{algorithm.lower()}_path.png",
            dpi=300,
            bbox_inches="tight"
        )

    if show:
        plt.show()

    plt.close()


def draw_performance_comparison(results, save=True, show=True):
    if not results:
        raise ValueError("No algorithm results were provided")

    algorithms = list(results.keys())

    metrics = [
        ("path_cost", "Path Cost"),
        ("trip_time", "Trip Time (minutes)"),
        ("nodes_generated", "Nodes Generated"),
        ("nodes_expanded", "Nodes Expanded"),
        ("max_frontier_size", "Maximum Frontier Size"),
        ("execution_time", "Execution Time (seconds)")
    ]

    fig, axes = plt.subplots(2, 3, figsize=(17, 10))

    for ax, (metric_key, metric_title) in zip(
        axes.flat, metrics
    ):
        values = [
            results[name].get(metric_key, 0)
            for name in algorithms
        ]

        if any(
            metric_key not in results[name]
            or results[name][metric_key] is None
            for name in algorithms
        ):
            ax.set_title(metric_title + " - Data unavailable")
            ax.axis("off")
            continue

        colors = [
            COLORS.get(name.upper(), "#7f8c8d")
            for name in algorithms
        ]

        bars = ax.bar(
            algorithms,
            values,
            color=colors
        )

        ax.set_title(metric_title)
        ax.set_ylabel(metric_title)
        ax.grid(axis="y", alpha=0.25)

        for bar, value in zip(bars, values):
            ax.annotate(
                f"{value:.6g}",
                (
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height()
                ),
                ha="center",
                va="bottom",
                fontsize=9
            )

        ax.margins(y=0.2)

    fig.suptitle(
        "Search Algorithms - Performance Comparison",
        fontsize=18,
        fontweight="bold"
    )

    plt.tight_layout()

    if save:
        plt.savefig(
            OUTPUT_DIR / "performance_comparison.png",
            dpi=300,
            bbox_inches="tight"
        )

    if show:
        plt.show()

    plt.close(fig)


def save_results_table(results):
    if not results:
        return

    filename = TABLE_DIR / "algorithm_comparison.csv"

    fields = [
        "algorithm",
        "path_cost",
        "trip_time",
        "nodes_generated",
        "nodes_expanded",
        "max_frontier_size",
        "execution_time"
    ]

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

        for algorithm, metrics in results.items():
            row = {"algorithm": algorithm}

            for field in fields[1:]:
                row[field] = metrics.get(field, "")

            writer.writerow(row)


if __name__ == "__main__":
    print("Generating Theme Park Map...")
    draw_park_map()

    print("Map saved successfully!")
