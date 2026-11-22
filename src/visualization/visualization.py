
"""Theme park maps, action timelines, and algorithm comparison plots."""

from pathlib import Path
import csv
from collections import Counter

import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.patches import Patch

from src.environment.environment import (
    LOCATIONS, PARK_EDGES, REQUIRED_ATTRACTIONS,
    TIME_LIMIT_MINUTES, TIME_LIMIT_UNITS, TIME_UNIT_MINUTES,
    get_successors, get_state_time_minutes,
)

GRAPH_DIR = Path("results/graphs")
TABLE_DIR = Path("results/tables")

COLORS = {
    "BFS": "#2878B5",
    "DFS": "#E28736",
    "UCS": "#2B9A66",
    "IDS": "#9663B5",
    "TEST": "#D64550"
}

METRICS = {
    "path_cost": "Path cost (15-minute units)",
    "estimated_trip_time_minutes": "Estimated trip time (minutes)",
    "nodes_generated": "Nodes generated",
    "nodes_expanded": "Nodes expanded",
    "max_frontier_size": "Max frontier size",
    "execution_time": "Execution time (seconds)"
}


def create_graph():
    graph = nx.Graph()
    graph.add_nodes_from(LOCATIONS)

    for start, end, minutes in PARK_EDGES:
        graph.add_edge(start, end, weight=minutes)

    return graph


def get_positions():
    # Fixed positions for consistent visualization.
    return {
        "Entrance": (-4.0, 0.4),
        "RollerCoaster": (-2.0, 2.2),
        "FerrisWheel": (-2.0, -2.2),
        "BumperCars": (0.1, 3.0),
        "HauntedHouse": (1.1, 1.6),
        "WaterRide": (1.2, -1.6),
        "DropTower": (0.0, -3.0),
        "FoodCourt": (-0.4, 0.1),
        "GiftShop": (3.0, 1.1),
        "Exit": (4.0, -1.8),
    }


def _base_graph(ax, graph, pos):
    nx.draw_networkx_edges(
        graph, pos, ax=ax,
        edge_color="#C7CDD3",
        width=1.5
    )

    node_colors = [
        "#29A56A" if n == "Entrance" else
        "#D94B4B" if n == "Exit" else
        "#4A91D3" if n in REQUIRED_ATTRACTIONS
        else "#E9BD54"
        for n in graph.nodes()
    ]

    nx.draw_networkx_nodes(
        graph, pos, ax=ax,
        node_color=node_colors,
        node_size=1900,
        edgecolors="white",
        linewidths=1.8
    )

    nx.draw_networkx_labels(
        graph, pos, ax=ax,
        font_size=8,
        font_weight="bold"
    )

    edge_labels = nx.get_edge_attributes(graph, "weight")

    nx.draw_networkx_edge_labels(
        graph, pos, ax=ax,
        edge_labels=edge_labels,
        font_size=8,
        rotate=False,
        bbox={
            "facecolor": "white",
            "edgecolor": "none",
            "alpha": 0.85
        }
    )

    ax.legend(
        handles=[
            Patch(color="#29A56A", label="Entrance"),
            Patch(color="#D94B4B", label="Exit"),
            Patch(color="#4A91D3", label="Required attraction"),
            Patch(color="#E9BD54", label="Other location")
        ],
        loc="upper left",
        fontsize=9
    )

    ax.set_axis_off()
    ax.margins(0.22)


def _finish(fig, filename, save=True, show=True):
    fig.tight_layout()

    if save:
        GRAPH_DIR.mkdir(parents=True, exist_ok=True)
        output = GRAPH_DIR / filename
        fig.savefig(output, dpi=220, bbox_inches="tight")
        print(f"Saved: {output}")

    if show:
        plt.show()

    plt.close(fig)


def draw_park_map(save=True, show=True):
    graph = create_graph()
    fig, ax = plt.subplots(figsize=(15, 9))

    _base_graph(ax, graph, get_positions())

    ax.set_title(
        f"Theme park network | "
        f"{TIME_LIMIT_MINUTES} min stated limit | "
        f"{TIME_LIMIT_UNITS * TIME_UNIT_MINUTES} min usable budget",
        fontsize=15,
        pad=20
    )

    ax.text(
        0.5, 0.02,
        "Edge labels = original walking time in minutes; "
        "search costs are rounded up separately to 15-minute units.",
        transform=ax.transAxes,
        ha="center",
        fontsize=9
    )

    _finish(fig, "theme_park_map.png", save, show)


def extract_locations(path):
    result = []

    for item in path:
        if isinstance(item, str):
            name = item
        elif isinstance(item, (tuple, list)) and len(item) == 3:
            name = item[0]
        else:
            raise ValueError(
                "Path entries must be location strings or 3-item states"
            )

        if name not in LOCATIONS:
            raise ValueError(f"Unknown location: {name}")

        result.append(name)

    return result


def get_path_actions(path):
    """Infer and validate actions from full state paths."""
    if not path:
        return []

    states = [tuple(state) for state in path]

    if any(len(state) != 3 for state in states):
        raise ValueError(
            "Full environment states are needed for actions"
        )

    actions = []

    for i, (previous, current) in enumerate(
        zip(states, states[1:]), start=1
    ):
        matched = [
            (act, cost)
            for nxt, act, cost in get_successors(previous)
            if nxt == current
        ]

        if not matched:
            raise ValueError(
                f"Invalid environment transition at step {i}"
            )

        action, cost = matched[0]

        actions.append({
            "step": i,
            "type": action[0],
            "location": action[1],
            "cost": cost,
            "time": get_state_time_minutes(current),
            "action": action
        })

    return actions


def draw_detailed_path(
    path, algorithm="BFS", save=True, show=True
):
    if not path:
        raise ValueError("No path to visualize")

    locations = extract_locations(path)

    full_states = all(
        isinstance(s, (tuple, list)) and len(s) == 3
        for s in path
    )

    actions = get_path_actions(path) if full_states else []

    graph = create_graph()
    pos = get_positions()
    color = COLORS.get(algorithm.upper(), "#D64550")

    fig, ax = plt.subplots(figsize=(16, 10))
    _base_graph(ax, graph, pos)

    move_steps = []

    for i, (start, end) in enumerate(
        zip(locations, locations[1:]), start=1
    ):
        if start == end:
            continue

        if not graph.has_edge(start, end):
            raise ValueError(
                f"Invalid edge: {start} -> {end}"
            )

        move_steps.append((i, start, end))

    repetitions = Counter(
        tuple(sorted((a, b)))
        for _, a, b in move_steps
    )

    seen = Counter()

    for step, start, end in move_steps:
        pair = tuple(sorted((start, end)))
        seen[pair] += 1

        occurrence = seen[pair]

        if repetitions[pair] == 1:
            radius = 0.0
        else:
            radius = (
                (0.13 + 0.13 * (occurrence - 1))
                * (1 if occurrence % 2 else -1)
            )

        x1, y1 = pos[start]
        x2, y2 = pos[end]

        ax.annotate(
            "",
            xy=(x2, y2),
            xytext=(x1, y1),
            arrowprops={
                "arrowstyle": "-|>",
                "color": color,
                "lw": 2.7,
                "mutation_scale": 18,
                "shrinkA": 31,
                "shrinkB": 31,
                "connectionstyle": f"arc3,rad={radius}"
            }
        )

    ax.set_title(
        f"{algorithm.upper()} route | {len(move_steps)} moves",
        fontsize=17,
        pad=18
    )

    if full_states:
        visited = [
            a["location"]
            for a in actions
            if a["type"] == "VISIT"
        ]

        final_time = get_state_time_minutes(
            tuple(path[-1])
        )

        ax.text(
            0.99, 0.03,
            f"Visits: {', '.join(visited) or 'none'}\n"
            f"Final estimated time: {final_time} min",
            transform=ax.transAxes,
            ha="right",
            va="bottom",
            fontsize=9,
            bbox={
                "facecolor": "white",
                "edgecolor": "#dddddd",
                "alpha": 0.95
            }
        )

    ax.text(
        0.01, 0.02,
        "Arrows show direction. "
        "For exact order/repeated edges, see Action Timeline.",
        transform=ax.transAxes,
        fontsize=9,
        bbox={
            "facecolor": "white",
            "edgecolor": "none",
            "alpha": 0.8
        }
    )

    _finish(
        fig,
        f"{algorithm.lower()}_detailed_path.png",
        save,
        show
    )


def draw_solution_path(
    path, algorithm="BFS", save=True, show=True
):
    return draw_detailed_path(
        path, algorithm, save, show
    )


def draw_action_timeline(
    path, algorithm="BFS", save=True, show=True
):
    actions = get_path_actions(path)

    if not actions:
        raise ValueError("Path has no actions")

    labels = [
        f"{a['step']:02d}. {a['type']} {a['location']}"
        for a in actions
    ]

    durations = [
        a["cost"] * TIME_UNIT_MINUTES
        for a in actions
    ]

    colors = [
        "#2B9A66" if a["type"] == "VISIT"
        else COLORS.get(algorithm.upper(), "#2878B5")
        for a in actions
    ]

    fig, ax = plt.subplots(
        figsize=(12, max(6, len(actions) * 0.46 + 2))
    )

    positions = list(range(len(actions)))

    bars = ax.barh(
        positions,
        durations,
        color=colors,
        height=0.66
    )

    ax.set_yticks(positions, labels=labels)
    ax.invert_yaxis()

    ax.set_xlabel(
        "Charged time per action (minutes, "
        "rounded up to 15-minute units)"
    )

    ax.set_title(
        f"{algorithm.upper()} action sequence",
        fontsize=16
    )

    ax.grid(axis="x", alpha=0.2)
    ax.set_axisbelow(True)
    ax.set_xlim(0, max(durations) * 1.55)

    for bar, duration in zip(bars, durations):
        ax.text(
            duration + 0.25,
            bar.get_y() + bar.get_height() / 2,
            f"{duration} min",
            va="center",
            fontsize=9
        )

    ax.legend(
        handles=[
            Patch(color="#2B9A66", label="VISIT"),
            Patch(
                color=COLORS.get(
                    algorithm.upper(), "#2878B5"
                ),
                label="MOVE"
            )
        ],
        loc="lower right"
    )

    _finish(
        fig,
        f"{algorithm.lower()}_timeline.png",
        save,
        show
    )


def draw_performance_comparison(
    results, save=True, show=True
):
    """Compare all algorithms, including unsuccessful ones."""
    if not results:
        raise ValueError("No results provided")

    names = list(results)

    fig, axes = plt.subplots(
        2, 3, figsize=(17, 10)
    )

    for ax, (key, title) in zip(
        axes.flat, METRICS.items()
    ):
        values = [
            results[name].get(key)
            for name in names
        ]

        existing = [
            (i, float(value))
            for i, value in enumerate(values)
            if isinstance(value, (int, float)) and value >= 0
        ]

        if existing:
            bars = ax.bar(
                [names[i] for i, _ in existing],
                [value for _, value in existing],
                color=[
                    COLORS.get(names[i].upper(), "#7C8592")
                    for i, _ in existing
                ]
            )

            for bar, (_, value) in zip(bars, existing):
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
            ax.grid(axis="y", alpha=0.2)
            ax.set_axisbelow(True)

        else:
            ax.text(
                0.5, 0.5,
                "N/A - no solution/data",
                transform=ax.transAxes,
                ha="center",
                va="center",
                fontsize=11
            )

        unavailable = [
            names[i]
            for i, value in enumerate(values)
            if value is None
        ]

        if unavailable and existing:
            ax.text(
                0.02, 0.98,
                "N/A: " + ", ".join(unavailable),
                transform=ax.transAxes,
                ha="left",
                va="top",
                fontsize=8,
                color="#555555"
            )

        ax.set_title(title, fontsize=11)
        ax.set_ylabel(title, fontsize=9)

    fig.suptitle(
        "Uninformed Search Performance - All Algorithms",
        fontsize=18
    )

    _finish(
        fig,
        "performance_comparison.png",
        save,
        show
    )


def save_results_table(results):
    TABLE_DIR.mkdir(parents=True, exist_ok=True)

    fields = [
        "algorithm",
        "status"
    ] + list(METRICS.keys())

    filename = TABLE_DIR / "algorithm_comparison.csv"

    with filename.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fields
        )

        writer.writeheader()

        for name, item in results.items():
            row = {
                "algorithm": name,
                "status": item.get(
                    "status",
                    "SUCCESS" if item.get("path")
                    else "NO_SOLUTION"
                )
            }

            row.update({
                key: item.get(key)
                for key in METRICS
            })

            writer.writerow(row)

    print(f"Saved: {filename}")
    return filename


if __name__ == "__main__":
    draw_park_map(show=False)
    print("Map ready.")
