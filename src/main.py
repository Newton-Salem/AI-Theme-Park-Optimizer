import sys
import importlib
import traceback
from pathlib import Path

import matplotlib
matplotlib.use("Agg")   # draw to files only, avoids window problems

# Make "src" importable even if started as: python src/main.py
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.environment.environment import TIME_UNIT_MINUTES
from src.visualization.integration import (
    generate_environment_map,
    process_algorithm_results,
)
from src.utils.metrics import print_metrics_comparison

# name -> (module, function). Each function takes no arguments.
ALGORITHMS = {
    "BFS": ("src.algorithms.bfs", "bfs"),
    "DFS": ("src.algorithms.dfs", "dfs"),
    "UCS": ("src.algorithms.ucs", "ucs"),
    "IDS": ("src.algorithms.ids", "ids"),
}


def run_all():
    results = {}
    for name, (module_name, func_name) in ALGORITHMS.items():
        try:
            func = getattr(importlib.import_module(module_name), func_name)
        except (ImportError, AttributeError) as error:
            print(f"[SKIP] {name}: cannot load ({error})")
            continue
        try:
            result = func()
        except Exception:
            print(f"[FAIL] {name}: crashed while running")
            traceback.print_exc()
            continue
        if not isinstance(result, dict):
            print(f"[FAIL] {name}: must return a dictionary")
            continue
        results[name] = result
        print(f"[OK]   {name} finished")
    return results


def save_solution_paths(results):
    out_dir = Path("results/tables")
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "solution_paths.txt", "w", encoding="utf-8") as f:
        for name, r in results.items():
            f.write(f"=== {name} ===\n")
            if not r.get("path"):
                f.write("No solution found\n\n")
                continue
            cost = r["path_cost"]
            f.write(f"Path cost: {cost} units = {cost * TIME_UNIT_MINUTES} min\n")
            actions = r.get("actions") or []
            for i, (state, action) in enumerate(zip(r["path"][1:], actions), 1):
                f.write(f"{i:>2}. {action[0]:<5} {action[1]:<14} -> {state}\n")
            f.write("\n")
    print("Saved:", out_dir / "solution_paths.txt")


def main():
    print("AI THEME PARK OPTIMIZER - PHASE I")
    generate_environment_map()
    results = run_all()
    if not results:
        print("No algorithm ran. Read the messages above.")
        return
    process_algorithm_results(results, show=False, draw_map=False)
    try:
        print_metrics_comparison(list(results.values()))
    except (ValueError, TypeError, KeyError) as error:
        print("Could not print comparison table:", error)
    save_solution_paths(results)
    print("\nDone. Open the 'results' folder.")


if __name__ == "__main__":
    main()