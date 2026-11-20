# 🎢 AI Theme Park Trip Optimizer

An Artificial Intelligence project that uses search algorithms to explore and optimize visitor routes inside a theme park.

The project provides a modular implementation of uninformed search algorithms, allowing different search strategies to operate on the same environment and be evaluated using consistent performance metrics.

## 📌 Project Overview

The AI Theme Park Trip Optimizer is developed using Python and follows a modular architecture that separates the environment, search algorithms, visualization, and performance evaluation.

The system represents the theme park as a graph-based environment and provides a common interface for search algorithms to explore possible routes and generate solutions.

The project is organized into independent modules to make the code easier to maintain, test, extend, and integrate.

## 🧠 Implemented Search Algorithms

The project focuses on implementing and comparing four uninformed search algorithms:

| Algorithm | Description |
|---|---|
| Breadth-First Search (BFS) | Explores states level by level using a FIFO queue. |
| Depth-First Search (DFS) | Explores one search branch as deeply as possible before backtracking. |
| Uniform Cost Search (UCS) | Expands the state with the lowest cumulative path cost. |
| Iterative Deepening Search (IDS) | Combines depth-limited DFS with progressively increasing depth limits. |

All algorithms operate on the same environment and use shared state representations, transition rules, and goal conditions to ensure consistency during evaluation.

## 📁 Project Structure

The repository follows a modular directory structure, with each component responsible for a specific part of the system.

```text
AI-Theme-Park-Optimizer/
│
├── src/
│   ├── environment/
│   │   └── environment.py
│   │
│   ├── algorithms/
│   │   ├── bfs.py
│   │   ├── dfs.py
│   │   ├── ucs.py
│   │   └── ids.py
│   │
│   ├── visualization/
│   │   └── visualization.py
│   │
│   ├── utils/
│   │   └── metrics.py
│   │
│   └── main.py
│
├── results/
│   ├── graphs/
│   └── tables/
│
├── docs/
│   ├── problem_model.md
│   ├── report.pdf
│   └── contribution_statement.md
│
├── README.md
├── requirements.txt
└── .gitignore
```

### Directory and Module Description

#### `src/environment/`

Contains the theme park environment implementation.

- **environment.py** – Defines the park structure, locations, connections, state representation, available actions, transition function, and goal conditions.

#### `src/algorithms/`

Contains the implementations of the uninformed search algorithms.

- **bfs.py** – Breadth-First Search implementation.
- **dfs.py** – Depth-First Search implementation.
- **ucs.py** – Uniform Cost Search implementation.
- **ids.py** – Iterative Deepening Search implementation.

Each algorithm uses the shared environment to explore possible states and search for valid solutions.

#### `src/visualization/`

Contains the visualization components.

- **visualization.py** – Responsible for presenting search results and visual representations of algorithm performance.

#### `src/utils/`

Contains shared utility functions.

- **metrics.py** – Handles the collection and calculation of search performance metrics, such as generated nodes, expanded nodes, frontier size, and execution time.

#### `src/main.py`

Serves as the main entry point of the application. It coordinates the execution of the implemented algorithms, collects their results, and connects the different project modules.

#### `results/`

Stores the output generated during algorithm execution and evaluation.

- **graphs/** – Contains performance graphs and visual comparisons.
- **tables/** – Contains structured performance results and comparison tables.

#### `docs/`

Contains the project's technical documentation and supporting reports.

- **problem_model.md** – Documents the formal problem formulation and environment specification.
- **report.pdf** – Contains the project report and evaluation results.
- **contribution_statement.md** – Documents the distribution of tasks and individual contributions.

## ⚙️ Technologies & Tools

- **Programming Language:** Python
- **Version Control:** Git & GitHub
- **Development Environment:** Visual Studio Code
- **Core Concepts:** Graph Representation, State-Space Search, Uninformed Search, Performance Analysis, and Algorithm Visualization.

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/Newton-Salem/AI-Theme-Park-Optimizer.git
```

### 2. Navigate to the Project Directory

```bash
cd AI-Theme-Park-Optimizer
```

### 3. Install Dependencies

Make sure Python is installed, then run:

```bash
pip install -r requirements.txt
```

### 4. Run the Project

Execute the main application from the repository root:

```bash
python -m src.main
```

## 📊 Performance Evaluation

The implemented algorithms are evaluated using a shared set of performance metrics to provide a fair comparison between different search strategies.

The evaluation includes:

- **Solution Path:** The sequence of actions leading to the goal.
- **Path Cost:** The total accumulated search cost.
- **Estimated Trip Time:** The estimated time required to complete the trip.
- **Nodes Generated:** The number of successor states generated.
- **Nodes Expanded:** The number of states whose successors are explored.
- **Maximum Frontier Size:** The maximum number of states stored in the frontier.
- **Execution Time:** The actual time taken by each algorithm to complete its search.

The collected results are used to generate comparison tables and performance graphs.

## 👥 Team Contributions

The project is developed collaboratively, with responsibilities divided among team members.

| Team Member | Responsibility |
|---|---|
| Person 1 | Problem Modeling and Environment Implementation |
| Person 2 | BFS and DFS Implementation |
| Person 3 | UCS and IDS Implementation |
| Person 4 | Visualization and Performance Graphs |
| Person 5 | Integration, Testing, and Documentation |

## 🔮 Future Development

The project is designed with extensibility in mind. Its modular architecture provides a foundation for introducing additional search techniques and optimization strategies.

Potential future extensions include:

- Informed Search Algorithms (Greedy Best-First Search and A*).
- Local Search Algorithms (Hill Climbing and Simulated Annealing).
- Genetic Algorithms.
- Advanced route optimization strategies.
- Additional visualization and performance analysis tools.

## 📄 Documentation

For more technical details about the environment design, state representation, transition model, constraints, and search problem formulation, refer to:

- `docs/problem_model.md`
- `docs/report.pdf`

---

**Course:** Artificial Intelligence (CSAI 301)  
**Project:** AI Theme Park Trip Optimizer  
**Phase:** Phase I – Uninformed Search

---
