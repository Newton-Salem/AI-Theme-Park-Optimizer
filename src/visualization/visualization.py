
from pathlib import Path
import csv

import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.patches import Patch

from src.environment.environment import (
    LOCATIONS,
    PARK_EDGES,
    REQUIRED_ATTRACTIONS,
    INITIAL_STATE,
    TIME_UNIT_MINUTES,
    TIME_LIMIT_MINUTES,
    FULL_VISITED_MASK,
    get_successors,
    get_state_time_minutes,
    is_goal
)


GRAPH_DIR = Path("results/graphs")
TABLE_DIR = Path("results/tables")

GRAPH_DIR.mkdir(parents=True, exist_ok=True)
TABLE_DIR.mkdir(parents=True, exist_ok=True)


COLORS = {
    "BFS": "#3498db",
    "DFS": "#e67e22",
    "UCS": "#27ae60",
    "IDS": "#9b59b6",
    "TEST": "#e74c3c"
}


METRICS = {
    "path_cost": "Path Cost (time units)",
    "estimated_trip_time_minutes": "Trip Time (minutes)",
    "nodes_generated": "Nodes Generated",
    "nodes_expanded": "Nodes Expanded",
    "max_frontier_size": "Maximum Frontier Size",
    "execution_time": "Execution Time (seconds)"
}


def create_graph():
    graph = nx.Graph()

    graph.add_nodes_from(LOCATIONS)

    for start, end, minutes in PARK_EDGES:
        graph.add_edge(start, end, weight=minutes)

    return graph


def get_positions():
    return {
        "Entrance": (-4, 0),
        "RollerCoaster": (-2, 2),
        "FerrisWheel": (-2, -2),
        "BumperCars": (0, 3),
        "HauntedHouse": (1, 1.5),
        "WaterRide": (1, -1.5),
        "DropTower": (0, -3),
        "FoodCourt": (-0.5, 0),
        "GiftShop": (3, 1),
        "Exit": (4, -2)
    }


def get_node_colors(graph):
    colors = []

    for node in graph.nodes():
        if node == "Entrance":
            colors.append("#2ecc71")
        elif node == "Exit":
            colors.append("#e74c3c")
        elif node in REQUIRED_ATTRACTIONS:
            colors.append("#3498db")
        else:
            colors.append("#f1c40f")

    return colors


def draw_base_graph(ax, graph, pos):
    nx.draw_networkx_edges(
        graph,
        pos,
        ax=ax,
        edge_color="#cbd5e1",
        width=1.5
    )

    nx.draw_networkx_nodes(
        graph,
        pos,
        ax=ax,
        node_color=get_node_colors(graph),
        node_size=2600,
        edgecolors="white",
        linewidths=2
    )

    nx.draw_networkx_labels(
        graph,
        pos,
        ax=ax,
        font_size=9,
        font_weight="bold"
    )

    edge_labels = nx.get_edge_attributes(
        graph, "weight"
    )

    nx.draw_networkx_edge_labels(
        graph,
        pos,
        ax=ax,
        edge_labels=edge_labels,
        font_size=8,
        bbox={
            "facecolor": "white",
            "edgecolor": "none",
            "alpha": 0.85
        }
    )

    ax.legend(
        handles=[
            Patch(color="#2ecc71", label="Entrance"),
            Patch(color="#e74c3c", label="Exit"),
            Patch(color="#3498db", label="Required Attraction"),
            Patch(color="#f1c40f", label="Other Location")
        ],
        loc="upper left"
    )

    ax.axis("off")
    ax.margins(0.15)


def finish_plot(fig, filename, save=True, show=True):
    fig.tight_layout()

    if save:
        fig.savefig(
            GRAPH_DIR / filename,
            dpi=300,
            bbox_inches="tight"
        )
        print("Saved:", GRAPH_DIR / filename)

    if show:
        plt.show()

    plt.close(fig)


def draw_park_map(save=True, show=True):
    graph = create_graph()
    pos = get_positions()

    fig, ax = plt.subplots(figsize=(16, 10))

    draw_base_graph(ax, graph, pos)

    ax.set_title(
        "AI Theme Park - Environment Map",
        fontsize=18,
        fontweight="bold",
        pad=20
    )

    finish_plot(
        fig,
        "theme_park_map.png",
        save,
        show
    )


def extract_locations(path):
    locations = []

    for item in path:
        if isinstance(item, str):
            location = item

        elif isinstance(item, (tuple, list)) and len(item) == 3:
            location = item[0]

        else:
            raise ValueError("Invalid path format")

        if location not in LOCATIONS:
            raise ValueError(
                f"Unknown location: {location}"
            )

        locations.append(location)

    return locations


def get_path_actions(path):
    actions = []

    for i in range(1, len(path)):
        previous = path[i - 1]
        current = path[i]

        if not (
            isinstance(previous, (tuple, list))
            and isinstance(current, (tuple, list))
            and len(previous) == 3
            and len(current) == 3
        ):
            raise ValueError(
                "Action extraction requires full environment states"
            )

        possible = get_successors(tuple(previous))

        matching = [
            (action, cost)
            for next_state, action, cost in possible
            if next_state == tuple(current)
        ]

        if not matching:
            raise ValueError(
                f"Invalid transition at step {i}"
            )

        action, cost = matching[0]

        actions.append({
            "step": i,
            "type": action[0],
            "location": action[1],
            "cost": cost,
            "time": get_state_time_minutes(current)
        })

    return actions


def draw_solution_path(path, algorithm="BFS",
                       save=True, show=True):
    return draw_detailed_path(
        path,
        algorithm=algorithm,
        save=save,
        show=show
    )


def draw_detailed_path(path, algorithm="BFS",
                       save=True, show=True):

    if not path:
        raise ValueError("Path cannot be empty")

    graph = create_graph()
    pos = get_positions()
    locations = extract_locations(path)

    color = COLORS.get(
        algorithm.upper(), "#e74c3c"
    )

    fig, ax = plt.subplots(figsize=(16, 10))

    draw_base_graph(ax, graph, pos)

    movement_number = 0

    for i in range(1, len(locations)):
        start = locations[i - 1]
        end = locations[i]

        if start == end:
            continue

        if not graph.has_edge(start, end):
            raise ValueError(
                f"Invalid movement: {start} -> {end}"
            )

        movement_number += 1

        x1, y1 = pos[start]
        x2, y2 = pos[end]

        ax.annotate(
            "",
            xy=(x2, y2),
            xytext=(x1, y1),
            arrowprops={
                "arrowstyle": "-|>",
                "color": color,
                "lw": 3,
                "mutation_scale": 20,
                "shrinkA": 30,
                "shrinkB": 30,
                "connectionstyle": "arc3,rad=0.12"
            }
        )

    visited = list(dict.fromkeys(locations))

    nx.draw_networkx_nodes(
        graph,
        pos,
        ax=ax,
        nodelist=visited,
        node_color=color,
        node_size=2600,
        edgecolors="white",
        linewidths=2
    )

    nx.draw_networkx_labels(
        graph,
        pos,
        ax=ax,
        font_size=9,
        font_weight="bold"
    )

    ax.set_title(
        f"{algorithm.upper()} - Search Route",
        fontsize=18,
        fontweight="bold",
        pad=20
    )

    ax.text(
        0.02,
        0.02,
        f"Movement steps: {movement_number}",
        transform=ax.transAxes,
        fontsize=11,
        bbox={
            "facecolor": "white",
            "edgecolor": "#dddddd"
        }
    )

    finish_plot(
        fig,
        f"{algorithm.lower()}_detailed_path.png",
        save,
        show
    )


def draw_action_timeline(path, algorithm="BFS",
                         save=True, show=True):

    actions = get_path_actions(path)

    if not actions:
        raise ValueError("No actions to display")

    labels = []
    colors = []
    durations = []

    for action in actions:
        label = (
            f"{action['step']}. "
            f"{action['type']} "
            f"{action['location']}"
        )

        labels.append(label)

        if action["type"] == "VISIT":
            colors.append("#27ae60")
        else:
            colors.append(
                COLORS.get(
                    algorithm.upper(),
                    "#3498db"
                )
            )

        durations.append(
            action["cost"] * TIME_UNIT_MINUTES
        )

    fig_height = max(6, len(actions) * 0.55 + 2)

    fig, ax = plt.subplots(
        figsize=(13, fig_height)
    )

    positions = list(range(len(actions)))

    bars = ax.barh(
        positions,
        durations,
        color=colors,
        height=0.65
    )

    ax.set_yticks(positions)
    ax.set_yticklabels(labels, fontsize=10)
    ax.invert_yaxis()

    ax.set_xlabel("Action Cost (minutes)")
    ax.set_title(
        f"{algorithm.upper()} - Action Timeline",
        fontsize=17,
        fontweight="bold"
    )

    ax.grid(axis="x", alpha=0.2)
    ax.set_axisbelow(True)

    for bar, duration in zip(bars, durations):
        ax.text(
            duration + 0.3,
            bar.get_y() + bar.get_height() / 2,
            f"{duration} min",
            va="center",
            fontsize=9
        )

    ax.set_xlim(0, max(durations) * 1.35)

    ax.legend(
        handles=[
            Patch(color="#27ae60", label="VISIT"),
            Patch(
                color=COLORS.get(
                    algorithm.upper(), "#3498db"
                ),
                label="MOVE"
            )
        ],
        loc="lower right"
    )

    finish_plot(
        fig,
        f"{algorithm.lower()}_timeline.png",
        save,
        show
    )


def draw_performance_comparison(results,
                                save=True, show=True):

    if not results:
        raise ValueError("No results provided")

    algorithms = list(results.keys())

    fig, axes = plt.subplots(
        2, 3,
        figsize=(18, 11)
    )

    for ax, (key, title) in zip(
        axes.flat, METRICS.items()
    ):
        values = [
            results[name].get(key)
            for name in algorithms
        ]

        if any(value is None for value in values):
            ax.set_title(title)
            ax.text(
                0.5, 0.5,
                "Data unavailable",
                ha="center",
                va="center",
                transform=ax.transAxes
            )
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

        ax.set_title(title)
        ax.set_ylabel(title)
        ax.grid(axis="y", alpha=0.2)
        ax.set_axisbelow(True)

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
        fontsize=20,
        fontweight="bold"
    )

    finish_plot(
        fig,
        "performance_comparison.png",
        save,
        show
    )


def save_results_table(results):
    if not results:
        return

    filename = TABLE_DIR / "algorithm_comparison.csv"

    fields = ["algorithm"] + list(METRICS.keys())

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

        for algorithm, data in results.items():
            row = {"algorithm": algorithm}

            for key in METRICS:
                row[key] = data.get(key, "")

            writer.writerow(row)

    print("Saved:", filename)


def build_test_path():
    test_actions = [
        ("MOVE", "FerrisWheel"),
        ("VISIT", "FerrisWheel"),
        ("MOVE", "WaterRide"),
        ("VISIT", "WaterRide"),
        ("MOVE", "HauntedHouse"),
        ("VISIT", "HauntedHouse"),
        ("MOVE", "BumperCars"),
        ("VISIT", "BumperCars"),
        ("MOVE", "RollerCoaster"),
        ("VISIT", "RollerCoaster")
    ]

    state = INITIAL_STATE
    path = [state]

    for wanted_action in test_actions:
        found = False

        for next_state, action, cost in get_successors(state):
            if action == wanted_action:
                state = next_state
                path.append(state)
                found = True
                break

        if not found:
            raise ValueError(
                f"Unavailable action: {wanted_action}"
            )

    return path


def run_demo():
    print("\nAI THEME PARK VISUALIZATION")
    print("----------------------------")

    print("\nGenerating park map...")
    draw_park_map(show=False)

    print("\nBuilding test path...")
    path = build_test_path()

    final_state = path[-1]

    print("Final state:", final_state)
    print("All attractions visited:",
          final_state[1] == FULL_VISITED_MASK)
    print("Goal reached:", is_goal(final_state))
    print(
        "Trip time:",
        get_state_time_minutes(final_state),
        "minutes"
    )
    print("Time limit:", TIME_LIMIT_MINUTES, "minutes")

    print("\nGenerating route visualization...")
    draw_detailed_path(
        path,
        algorithm="TEST",
        show=False
    )

    print("\nGenerating action timeline...")
    draw_action_timeline(
        path,
        algorithm="TEST",
        show=False
    )

    print("\nDemo completed successfully.")
    print("Images saved in:", GRAPH_DIR)


if __name__ == "__main__":
    run_demo()
