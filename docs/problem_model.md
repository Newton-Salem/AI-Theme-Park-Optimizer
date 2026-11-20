# AI Theme Park Trip Optimizer
## Problem Modeling and Environment Specification

**Project:** AI Theme Park Trip Optimizer  
**Course:** Artificial Intelligence (CSAI 301)  
**Phase:** Phase I – Uninformed Search  
**Document:** Problem Model  
**Programming Language:** Python  

---

# 1. Introduction

The AI Theme Park Trip Optimizer is an artificial intelligence project that aims to find suitable routes for visitors inside a theme park while considering a limited amount of available time.

Visitors typically want to experience several attractions during their visit. However, each attraction may have a different waiting time, ride duration, and location. Additionally, moving between attractions requires time.

The objective of this project is to model the theme park as a search problem and apply uninformed search algorithms to find valid routes that satisfy the visitor's requirements.

The system will implement and compare the following algorithms:

- Breadth-First Search (BFS)
- Depth-First Search (DFS)
- Uniform Cost Search (UCS)
- Iterative Deepening Search (IDS)

The primary optimization objective is to minimize the total estimated time required to visit all required attractions and reach the park exit without exceeding the visitor's time budget.

---

# 2. Problem Description

Consider a visitor entering a theme park with a maximum available time of **180 minutes (3 hours)**.

The park contains ten locations, including:

- An entrance.
- An exit.
- Five required attractions.
- Three additional optional locations.

Each required attraction has:

1. A location within the park.
2. A queue or waiting time.
3. A ride duration.

Moving between connected locations also requires time.

The visitor must:

1. Start at the Entrance.
2. Visit all five required attractions.
3. Return to the Exit.
4. Complete the trip within the available time budget.

The search algorithms explore possible sequences of movements and attraction visits to identify valid solutions.

A solution is considered valid only when every required attraction has been visited and the visitor reaches the Exit within the time limit.

---

# 3. Environment Design

## 3.1 Theme Park Locations

The environment consists of ten distinct locations.

| ID | Location | Type | Required? |
|---|---|---|---|
| 1 | Entrance | Starting Point | Yes |
| 2 | RollerCoaster | Attraction | Yes |
| 3 | FerrisWheel | Attraction | Yes |
| 4 | BumperCars | Attraction | Yes |
| 5 | HauntedHouse | Attraction | Yes |
| 6 | WaterRide | Attraction | Yes |
| 7 | DropTower | Optional Location | No |
| 8 | FoodCourt | Optional Location | No |
| 9 | GiftShop | Optional Location | No |
| 10 | Exit | Destination | Yes |

The five required attractions are:

1. RollerCoaster
2. FerrisWheel
3. BumperCars
4. HauntedHouse
5. WaterRide

The visitor must visit all five required attractions before reaching the Exit.

The optional locations can be used as intermediate locations when moving through the park. Visiting them is not required to satisfy the goal condition.


## 3.2 Park Representation as a Graph

The theme park is represented as a weighted, undirected graph:

\[
G = (V,E)
\]

Where:

- \(V\) represents the set of park locations.
- \(E\) represents the connections between locations.
- Each edge has a positive weight representing travel time in minutes.

The graph is undirected because movement between connected locations is assumed to be possible in both directions with the same travel time.

### Graph Vertices

\[
V =
\{
Entrance,
RollerCoaster,
FerrisWheel,
BumperCars,
HauntedHouse,
WaterRide,
DropTower,
FoodCourt,
GiftShop,
Exit
\}
\]

Therefore:

\[
|V| = 10
\]

### Graph Edges and Travel Times

The following table defines the proposed park connections.

| From | To | Travel Time |
|---|---|---:|
| Entrance | RollerCoaster | 5 min |
| Entrance | FerrisWheel | 8 min |
| Entrance | GiftShop | 4 min |
| RollerCoaster | BumperCars | 6 min |
| RollerCoaster | HauntedHouse | 7 min |
| RollerCoaster | FoodCourt | 9 min |
| FerrisWheel | WaterRide | 5 min |
| FerrisWheel | FoodCourt | 4 min |
| FerrisWheel | DropTower | 6 min |
| BumperCars | HauntedHouse | 4 min |
| BumperCars | FoodCourt | 7 min |
| HauntedHouse | WaterRide | 8 min |
| HauntedHouse | GiftShop | 5 min |
| WaterRide | DropTower | 4 min |
| WaterRide | Exit | 9 min |
| DropTower | Exit | 6 min |
| FoodCourt | GiftShop | 3 min |
| FoodCourt | Exit | 8 min |
| GiftShop | Exit | 5 min |

All travel times are positive.

The graph is connected, meaning that every location can be reached from every other location through one or more valid connections.

The graph is not fully connected. A visitor can only move directly between locations that share an edge.

---

# 4. Attraction Service Times

Reaching an attraction does not automatically mean that the visitor has experienced it.

The visitor must perform a separate Visit action.

Each required attraction has a queue time and a ride duration.

The following values represent the assumed environment configuration for this project.

| Attraction | Queue Time | Ride Duration | Total Service Time |
|---|---:|---:|---:|
| RollerCoaster | 15 min | 5 min | 20 min |
| FerrisWheel | 10 min | 5 min | 15 min |
| BumperCars | 10 min | 5 min | 15 min |
| HauntedHouse | 10 min | 5 min | 15 min |
| WaterRide | 15 min | 5 min | 20 min |

The total service time is calculated as:

\[
ServiceTime(a) = QueueTime(a) + RideDuration(a)
\]

For example:

\[
ServiceTime(RollerCoaster) = 15 + 5 = 20
\]

The queue and ride durations are assumed to be fixed throughout the search process.

This assumption allows all algorithms to operate on the same deterministic environment.

---

# 5. Problem Formulation

The problem is formulated as a state-space search problem.

A search problem is defined by:

1. State Space
2. Initial State
3. Actions
4. Transition Function
5. Goal Test
6. Path Cost

Each component is described below.

---

# 6. State Space Representation

## 6.1 Definition of a State

A state represents the complete relevant situation of the visitor at a particular point during the trip.

Each state contains three components:

\[
S = (L,M,T)
\]

Where:

- \(L\): Current location.
- \(M\): Visited attractions representation.
- \(T\): Elapsed time represented in 15-minute units.

Therefore, the state is:

\[
S = (CurrentLocation, VisitedMask, TimeUnits)
\]

### 1. Current Location

Represents the visitor's current position within the park.

Possible values are the ten locations defined in the environment.

### 2. Visited Attractions

The five required attractions are represented using a binary bitmask.

Each bit indicates whether a particular attraction has been visited.

The attraction-to-bit mapping is:

| Attraction | Bit Position | Bit Value |
|---|---:|---:|
| RollerCoaster | 0 | 1 |
| FerrisWheel | 1 | 2 |
| BumperCars | 2 | 4 |
| HauntedHouse | 3 | 8 |
| WaterRide | 4 | 16 |

A bit value of 1 means that the corresponding attraction has been visited.

A bit value of 0 means that it has not been visited.

The mask is updated using the bitwise OR operator.

For example:

\[
M_{new} = M_{old} | AttractionBit
\]

If the visitor has visited RollerCoaster and BumperCars:

\[
M = 1 + 4 = 5
\]

In binary:

\[
M = 00101_2
\]

The complete mask indicating that all five required attractions have been visited is:

\[
M_{goal} = 11111_2 = 31
\]

This representation allows the system to track visited attractions efficiently.

### 3. Elapsed Time

The visitor has a maximum time budget of 180 minutes.

To keep the state space finite and manageable, time is discretized into 15-minute units.

\[
TimeUnit = 15 {minutes}
\]

The time representation is:

\[
T = {ElapsedTime}/{15}
\]

The possible time values are:

\[
T \{0,1,2,....,12\}
\]

Each time unit represents 15 minutes.

For example:

| Time Units | Estimated Elapsed Time |
|---:|---:|
| 0 | 0 min |
| 1 | 15 min |
| 2 | 30 min |
| 3 | 45 min |
| 4 | 60 min |
| 5 | 75 min |
| 6 | 90 min |
| 7 | 105 min |
| 8 | 120 min |
| 9 | 135 min |
| 10 | 150 min |
| 11 | 165 min |
| 12 | 180 min |

The estimated elapsed time is calculated as:

\[
ElapsedTime = T X 15
\]

### Example State

Consider the following state:

\[
S = (RollerCoaster,5,3)
\]

This means:

- The visitor is currently at RollerCoaster.
- RollerCoaster and BumperCars have been visited.
- The estimated elapsed time is 45 minutes.

The state contains all information required to determine the visitor's possible future actions.

## 6.2 Why Is the State Representation Important?

Two states at the same location are not necessarily identical.

For example:

\[
S_1 = (FerrisWheel,1,3)
\]

\[
S_2 = (FerrisWheel,5,3)
\]

Both states represent a visitor at FerrisWheel after 45 minutes.

However:

- In \(S_1\), only RollerCoaster has been visited.
- In \(S_2\), RollerCoaster and BumperCars have been visited.

These states have different future possibilities because they represent different progress toward the goal.

Therefore, the current location alone is insufficient to describe the problem.

The visited-attractions mask and elapsed time must also be included.

---

# 7. Initial State

The initial state represents the visitor immediately after entering the theme park.

Initially:

- The visitor is at Entrance.
- No required attractions have been visited.
- No time has been consumed.

Therefore:

\[
S_0 = (Entrance,0,0)
\]

In Python-style notation:

```python
initial_state = ("Entrance", 0, 0)
```

This state is the starting node for all four search algorithms.

All algorithms must use the same initial state to ensure a fair comparison.

---

# 8. Goal State

The goal state represents a successful theme park trip.

A state is considered a goal if and only if all the following conditions are satisfied:

1. The visitor has visited all five required attractions.
2. The visitor is currently at the Exit.
3. The elapsed time does not exceed 180 minutes.

The goal conditions are:

\[
Location = Exit
\]

\[
VisitedMask = 31
\]

\[
ElapsedTime = 180
\]

Using time units:

\[
T = 12
\]

The goal test can be expressed mathematically as:

\[
Goal(S) =
(Location = Exit)
&
(VisitedMask = 31)
&
(T <= 12)
\]

### Python Representation

```python
def is_goal(state):
    location, visited_mask, time_units = state

    return (
        location == "Exit"
        and visited_mask == 31
        and time_units <= 12
    )
```

A visitor reaching the Exit without visiting all required attractions is not considered a successful solution.

Similarly, visiting all required attractions without reaching the Exit is not a goal state.

---

# 9. Actions

Actions represent the operations available to the visitor.

There are two main action categories.

## 9.1 Move Action

The visitor can move from the current location to an adjacent location.

A movement is valid only if a direct connection exists between the two locations in the park graph.

For example:

\[
Move(Entrance,RollerCoaster)
\]

The travel cost is:

\[
Cost = 5 { minutes}
\]

A Move action:

1. Changes the current location.
2. Adds the travel time to the elapsed time.
3. Does not change the visited-attractions mask.

The movement action does not automatically mark an attraction as visited.

## 9.2 Visit Attraction Action

If the visitor is currently at a required attraction that has not yet been visited, the visitor can perform a Visit action.

For example:

\[
Visit(RollerCoaster)
\]

The action consumes:

\[
Cost = QueueTime + RideDuration
\]

For RollerCoaster:

\[
Cost = 15 + 5 = 20 {minutes}
\]

A Visit action:

1. Keeps the visitor at the same location.
2. Adds the attraction's service time(cost) to the elapsed time.
3. Updates the visited-attractions mask.

The attraction cannot be visited again once its corresponding bit has been set.

## 9.3 Invalid Actions

The following actions are not allowed:

- Moving to a location without a direct graph connection.
- Visiting an attraction from a different location.
- Visiting an already visited required attraction.
- Exceeding the maximum time budget.
- Moving after reaching a valid goal state.

## 9.4 Action Summary

| Action | Preconditions | State Changes |
|---|---|---|
| Move to Neighbor | A direct connection exists | Updates location and time |
| Visit Attraction | Current location is an unvisited required attraction | Updates visited mask and time |

These actions define the legal operations available to all search algorithms.

---

# 10. Transition Function

The transition function determines the resulting state after performing a valid action.

It is defined as:

\[
Result(S,A) = S'
\]

Where:

- \(S\) is the current state.
- \(A\) is a valid action.
- \(S'\) is the resulting state.

The transition function has two cases.

## 10.1 Transition After a Move Action

Suppose the current state is:

\[
S = (L,M,T)
\]

The visitor moves to an adjacent location \(L'\).

Let:

\[
TravelTime(L,L') = d
\]

The new time cost in discretized units is:

\[
CostUnits =
{d}/{15}
\]

The resulting state is:

\[
S' = (L',M,T+CostUnits)
\]

The visited-attractions mask remains unchanged.

### Example

Suppose the visitor is at Entrance:

\[
S = (Entrance,0,0)
\]

The visitor moves to RollerCoaster.

The travel time is 5 minutes.

Therefore:

\[
CostUnits = {5}/{15} = 1
\]

The resulting state is:

\[
S' = (RollerCoaster,0,1)
\]

The estimated elapsed time is 15 minutes.

## 10.2 Transition After a Visit Action

Suppose the visitor is currently at a required attraction \(A\).

Let:

\[
ServiceTime(A) = QueueTime(A) + RideDuration(A)
\]

The time cost in units is:

\[
CostUnits =
{ServiceTime(A)}/{15}
\]

The attraction's bit value is represented by:

\[
Bit(A)
\]

The new visited mask is:

\[
M' = M|Bit(A)
\]

The resulting state is:

\[
S' = (L,M',T+CostUnits)
\]

The location remains unchanged.

### Example

Suppose the visitor is at RollerCoaster and has not visited it yet.

Current state:

\[
S = (RollerCoaster,0,1)
\]

The service time is:

\[
15+5=20 {minutes}
\]

Therefore:

\[
CostUnits = {20}/{15} = 2
\]

The RollerCoaster bit value is:

\[
Bit(RollerCoaster)=1
\]

The new visited mask becomes:

\[
M'=0|1=1
\]

The resulting state is:

\[
S'=(RollerCoaster,1,3)
\]

The estimated elapsed time is now 45 minutes.

## 10.3 Time Limit Validation

A transition is valid only if:

\[
T'<= 12
\]

Any successor state that exceeds the maximum time budget is discarded.

This ensures that the search algorithms do not explore states representing trips longer than 180 minutes.

## 10.4 Time Discretization Policy

Actual travel and service durations are not necessarily multiples of 15 minutes.

To maintain a finite and consistent state representation, each individual action duration is rounded upward to the next 15-minute unit.

The rounding formula is:

\[
RoundedCost(d)=
up ceil {d}/{15}
\]

For example:

| Actual Action Duration | Discretized Cost |
|---:|---:|
| 3 min | 15 min |
| 5 min | 15 min |
| 10 min | 15 min |
| 15 min | 15 min |
| 16 min | 30 min |
| 20 min | 30 min |
| 30 min | 30 min |

This is a conservative approximation because it may slightly overestimate the actual time required.

**Important:** The same discretization policy must be applied consistently in all four algorithms.

The reported path cost will represent the discretized estimated time, not an exact real-world duration.

---

# 11. Step Cost and Path Cost

The cost of an action represents the time consumed by that action.

There are two possible types of action costs:

### Movement Cost

\[
C_{move}(L,L') =
round up {TravelTime(L,L')}/{15}
\]

### Attraction Visit Cost

\[
C_{visit}(A) =
round up {QueueTime(A)+RideDuration(A)}/{15}
\]

The path cost is the sum of the costs of all actions performed along the path.

\[
g(n)=\sum_{i=1}^{k}C(a_i)
\]

Where:

- \(g(n)\) is the cumulative path cost.
- \(C(a_i)\) is the discretized cost of action \(i\).
- \(k\) is the number of actions performed.

The estimated total time is:

\[
TotalTime = 15 \times g(n)
\]

The optimization objective is:

\[
\boxed{
\min \sum_{i=1}^{k}C(a_i)
}
\]

Subject to:

\[
TotalTime <= 180
\]

The search problem therefore aims to find a valid goal state with the minimum discretized total time.

This cost definition is particularly important for Uniform Cost Search.

---

# 12. State Space Size Estimation

The state space size represents the number of theoretically possible states in the environment.

The state contains three independent components:

1. Current location.
2. Visited-attractions mask.
3. Discretized elapsed time.

## 12.1 Number of Locations

There are ten locations:

\[
|L|=10
\]

## 12.2 Number of Visited-Attraction Combinations

There are five required attractions.

Each attraction can either be visited or not visited.

Therefore:

\[
|M|=2^5=32
\]

## 12.3 Number of Time Values

The maximum time budget is 180 minutes.

The time unit is 15 minutes.

Therefore:

\[
|T|={180}/{15}+1=13
\]

The additional 1 accounts for the initial time value of zero.

The possible values are:

\[
T=\{0,1,2,.....,12\}
\]

## 12.4 Total Theoretical State Space

The maximum theoretical state space size is:

\[
|S|=|L| X |M| X |T|
\]

Substituting:

\[
|S|=10 X 32 X 13
\]

Therefore:

\[
{|S|=4160}
\]

The theoretical state space contains **4,160 possible state combinations**.

This value is within the required range of 1,000 to 10,000 states.

## 12.5 Reachable States

The value of 4,160 represents an upper bound, not necessarily the exact number of reachable states.

Some combinations may be unreachable because:

- The graph only permits movement along existing edges.
- Time cannot exceed the maximum budget.
- Certain combinations of locations and visited attractions may not be reachable through valid actions.
- Some states may be eliminated because their required actions exceed the remaining time.

The actual number of reachable states should be calculated programmatically by exploring the environment from the initial state while respecting all valid transitions and the time limit.

The theoretical state space size and the actual reachable state count will be reported separately.

---

# 13. Search Problem Properties

The environment has the following characteristics:

| Property | Description |
|---|---|
| Environment | Fully observable |
| Environment Type | Deterministic |
| State Space | Finite |
| Action Space | Discrete |
| Transition Model | Deterministic |
| Path Costs | Positive |
| Search Type | Uninformed Search |
| Objective | Minimize estimated total trip time |
| Time Constraint | 180 minutes |
| Number of Locations | 10 |
| Required Attractions | 5 |
| Time Discretization | 15 minutes |

The environment is deterministic because the same state and action always produce the same resulting state.

It is fully observable because the system has complete information about the visitor's location, visited attractions, and elapsed time.

It is finite because the number of locations, visited-attraction combinations, and time values is bounded.

---

# 14. Assumptions and Constraints

The following assumptions define the environment and ensure consistent behavior across all search algorithms.

## 14.1 Park Environment Assumptions

1. The theme park contains exactly ten predefined locations.
2. The park is represented as a weighted, undirected graph.
3. Movement is only allowed between directly connected locations.
4. All connections have positive travel times.
5. All required attractions are available throughout the trip.
6. The park does not close during the visitor's trip.

## 14.2 Attraction Assumptions

7. There are exactly five required attractions.
8. Each required attraction must be visited exactly once.
9. Visiting an attraction includes both its queue time and ride duration.
10. Queue times and ride durations remain constant.
11. Optional locations are not required for a successful trip.
12. Optional locations do not add service time in at the moment (phase 1) but we may add in phase 2.

## 14.3 Time Assumptions

13. The maximum available trip time is 180 minutes.
14. Time is discretized into 15-minute units.
15. Each action duration is rounded upward to the next 15-minute unit.
16. The visitor cannot exceed the maximum time budget.
17. The estimated elapsed time is the sum of discretized action costs.

## 14.4 Search Assumptions

18. All algorithms use the same environment and initial state.
19. All algorithms use the same goal test.
20. Every algorithm must generate successors using the same transition rules.
21. The search process must avoid repeatedly exploring identical states.
22. Parent tracking is used to reconstruct the solution path.
23. All reported performance measurements must be obtained from actual program execution.

## 14.5 Scope Limitations

This phase (phase 1) environment does not consider:

- Random or changing queue times.
- Ride breakdowns.
- Weather conditions.
- Visitor preferences.
- Attraction popularity.
- Variable walking speeds.
- Dynamic changes in travel time.

These features may be considered in future extensions, but they are excluded from the initial deterministic model.

---

# 15. Successor Function

The successor function returns all valid states that can be reached from the current state through one legal action.

It is defined as:

\[
Successors(S)=\{S' \mid S' = Result(S,A)\}
\]

For a given state, the function performs the following operations:

1. Identify all locations directly connected to the current location.
2. Generate valid movement actions.
3. Check whether the current location is an unvisited required attraction.
4. If possible, generate a Visit action.
5. Calculate the discretized time cost of each action.
6. Reject any successor that exceeds the time budget.
7. Return the remaining valid successor states.

Each successor should also provide the action performed and its step cost so that the search algorithms can reconstruct the solution and calculate path costs.

The successor function must be shared by all four search algorithms to guarantee that they operate on exactly the same problem definition.

---

# 16. Solution Representation

A solution is a sequence of states and actions that starts at the initial state and ends at a valid goal state.

A solution path can be represented as:

\[
P=(S_0,A_1,S_1,A_2,......,A_k,S_k)
\]

Where:

- \(S_0\) is the initial state.
- \(A_i\) represents an action.
- \(S_i\) represents the resulting state.
- \(S_k\) is a valid goal state.

The solution must satisfy all of the following:

- It begins at Entrance.
- It visits all five required attractions.
- It reaches Exit.
- It does not exceed the time budget.
- Every transition is valid according to the park graph and transition function.

The final path should display both movement and attraction visits.

For example, a path should distinguish between:

```text
Entrance
    |
    | Move
    v
RollerCoaster
    |
    | Visit Attraction
    v
RollerCoaster (Visited)
    |
    | Move
    v
FerrisWheel
    |
    | Visit Attraction
    v
FerrisWheel (Visited)
```

This distinction is important because moving to an attraction and visiting it are two different actions.

---

# 17. Relationship to Uninformed Search Algorithms

The environment is designed to support the four uninformed search algorithms required in thi phase (Phase 1).

All algorithms will receive:

- The same initial state.
- The same successor function.
- The same goal test.
- The same action costs.
- The same time constraints.

## 17.1 Breadth-First Search (BFS)

BFS explores the state space level by level.

It uses a FIFO queue.

In this problem, BFS finds a solution with the smallest number of actions, provided it is implemented with correct repeated-state handling.

However, because action costs are not equal, BFS does not guarantee the minimum total travel and service time.

## 17.2 Depth-First Search (DFS)

DFS explores one branch as deeply as possible before backtracking.

It uses a LIFO stack.

DFS may find a valid solution without exploring the entire state space, but the solution is not guaranteed to have the lowest cost or smallest depth.

Because the modeled state space is finite and repeated states are handled correctly, graph-search DFS can be complete in this environment.

## 17.3 Uniform Cost Search (UCS)

UCS expands the state with the lowest cumulative path cost.

It uses a priority queue ordered by path cost.

Since the project defines positive action costs, UCS can find a minimum-cost solution if one exists and the implementation correctly handles improved paths to previously discovered states.

UCS is the primary algorithm for minimizing the total discretized trip time.

## 17.4 Iterative Deepening Search (IDS)

IDS repeatedly performs depth-limited DFS with increasing depth limits.

For example:

- Depth limit 0.
- Depth limit 1.
- Depth limit 2.
- Depth limit 3.
- Continue until a goal is found or a defined maximum depth is reached.

IDS combines the low memory requirements of DFS with the shallowest-solution property of BFS under the usual finite-branching assumptions.

However, it does not guarantee minimum total time when action costs differ.

---

# 18. Performance Evaluation Metrics

Each search algorithm will be evaluated using the same performance metrics.

| Metric | Description |
|---|---|
| Solution Path | The sequence of states and actions leading to the goal |
| Path Cost | Total discretized cost of the solution |
| Estimated Trip Time | Path cost multiplied by 15 minutes |
| Nodes Generated | Number of successor states generated |
| Nodes Expanded | Number of states whose successors are explored |
| Maximum Frontier Size | Maximum number of states stored in the frontier at any point |
| Running Time | Actual execution time measured in seconds |

For fair comparison, the team must use consistent definitions of generated and expanded nodes across all algorithms.

The exact counting convention must be documented in the algorithm implementation and used consistently in the final results.

Running time must be measured using actual program execution rather than manually assigned values.

---

# 19. Modeling Limitations and Future Extensions

The current model is intentionally deterministic and uses fixed costs to make the problem suitable for comparing uninformed search algorithms.

The same state representation may be extended in Phase 2.

Potential extensions include:

- Adding heuristic functions to estimate the remaining trip cost.
- Implementing Greedy Best-First Search.
- Implementing A* Search.
- Applying Hill Climbing to improve attraction visit orders.
- Applying Simulated Annealing to explore alternative routes.
- Applying Genetic Algorithms to optimize complete trip plans.
- Introducing visitor preferences and attraction priorities.
- Modeling dynamic queue times and changing conditions.

The current model provides a common environment for both phases, reducing the need to redesign the problem when additional algorithms are introduced.

---

# 20. Conclusion

The AI Theme Park Trip Optimizer models a visitor's journey through a theme park as a finite, deterministic, weighted state-space search problem.

Each state represents the visitor's current location, visited required attractions, and discretized elapsed time.

The initial state places the visitor at the Entrance with no attractions visited and zero elapsed time.

The goal state requires the visitor to visit all five required attractions and reach the Exit without exceeding 180 minutes.

The environment provides two main actions: moving between connected locations and visiting the attraction at the current location.

All action costs are positive and are measured using a consistent 15-minute discretization policy.

The theoretical state space contains 4,160 possible state combinations, which satisfies the required state-space size range.

This formulation provides a consistent foundation for implementing and comparing BFS, DFS, UCS, and IDS in Phase 1, while also supporting the informed and local search algorithms planned for Phase 2.