import math


# Basic settings
TIME_UNIT_MINUTES = 15
TIME_LIMIT_MINUTES = 220
TIME_LIMIT_UNITS = TIME_LIMIT_MINUTES // TIME_UNIT_MINUTES #12

LOCATIONS = [
    "Entrance",
    "RollerCoaster",
    "FerrisWheel",
    "BumperCars",
    "HauntedHouse",
    "WaterRide",
    "DropTower",
    "FoodCourt",
    "GiftShop",
    "Exit"
]


# Required attractions and their bit positions
REQUIRED_ATTRACTIONS = {
    "RollerCoaster": 0,  #1
    "FerrisWheel": 1,    #2
    "BumperCars": 2,     #4
    "HauntedHouse": 3,   #8
    "WaterRide": 4       #16  

    # Total: 31 in decimal, 11111 in binary, which is 2^5 - 1  (meaning all 5 attractions visited)
}

FULL_VISITED_MASK = (1 << len(REQUIRED_ATTRACTIONS)) - 1 

# Attraction times in minutes
QUEUE_TIMES = {
    "RollerCoaster": 15,
    "FerrisWheel": 10,
    "BumperCars": 10,
    "HauntedHouse": 10,
    "WaterRide": 15
}

RIDE_DURATIONS = {
    "RollerCoaster": 5,
    "FerrisWheel": 5,
    "BumperCars": 5,
    "HauntedHouse": 5,
    "WaterRide": 5
}


# Connections between park locations
PARK_EDGES = [
    ("Entrance", "RollerCoaster", 5),
    ("Entrance", "FerrisWheel", 8),
    ("Entrance", "GiftShop", 4),
    ("RollerCoaster", "BumperCars", 6),
    ("RollerCoaster", "HauntedHouse", 7),
    ("RollerCoaster", "FoodCourt", 9),
    ("FerrisWheel", "WaterRide", 5),
    ("FerrisWheel", "FoodCourt", 4),
    ("FerrisWheel", "DropTower", 6),
    ("BumperCars", "HauntedHouse", 4),
    ("BumperCars", "FoodCourt", 7),
    ("HauntedHouse", "WaterRide", 8),
    ("HauntedHouse", "GiftShop", 5),
    ("WaterRide", "DropTower", 4),
    ("WaterRide", "Exit", 9),
    ("DropTower", "Exit", 6),
    ("FoodCourt", "GiftShop", 3),
    ("FoodCourt", "Exit", 8),
    ("GiftShop", "Exit", 5)
]


# Build the undirected graph
PARK_GRAPH = {location: {} for location in LOCATIONS}

for start, end, travel_time in PARK_EDGES:
    PARK_GRAPH[start][end] = travel_time
    PARK_GRAPH[end][start] = travel_time


# Initial state: (current_location, visited_mask, time_units)
INITIAL_STATE = ("Entrance", 0, 0)


def minutes_to_units(minutes):
    return math.ceil(minutes / TIME_UNIT_MINUTES)


def is_valid_state(state):
    if not isinstance(state, tuple) or len(state) != 3:
        return False

    location, visited_mask, time_units = state

    if location not in LOCATIONS:
        return False

    if type(visited_mask) is not int:
        return False

    if type(time_units) is not int:
        return False

    if not 0 <= visited_mask <= FULL_VISITED_MASK:
        return False

    if not 0 <= time_units <= TIME_LIMIT_UNITS:
        return False

    return True


def is_goal(state):
    if not is_valid_state(state):
        return False

    location, visited_mask, time_units = state

    return (
        location == "Exit"
        and visited_mask == FULL_VISITED_MASK
        and time_units <= TIME_LIMIT_UNITS
    )


def get_successors(state):
    successors = []

    if not is_valid_state(state):
        return successors

    if is_goal(state):
        return successors

    location, visited_mask, time_units = state

    # Visit the current attraction if it has not been visited
    if location in REQUIRED_ATTRACTIONS:
        attraction_index = REQUIRED_ATTRACTIONS[location]
        attraction_bit = 1 << attraction_index

        if not (visited_mask & attraction_bit):
            service_time = (
                QUEUE_TIMES[location] + RIDE_DURATIONS[location]
            )

            step_cost = minutes_to_units(service_time)
            new_time = time_units + step_cost

            if new_time <= TIME_LIMIT_UNITS:
                new_mask = visited_mask | attraction_bit

                new_state = (
                    location,
                    new_mask,
                    new_time
                )

                action = ("VISIT", location)

                successors.append(
                    (new_state, action, step_cost)
                )

    # Move to connected locations
    for neighbor, travel_time in PARK_GRAPH[location].items():
        step_cost = minutes_to_units(travel_time)
        new_time = time_units + step_cost

        if new_time <= TIME_LIMIT_UNITS:
            new_state = (
                neighbor,
                visited_mask,
                new_time
            )

            action = ("MOVE", neighbor)

            successors.append(
                (new_state, action, step_cost)
            )

    return successors


def get_state_time_minutes(state):
    return state[2] * TIME_UNIT_MINUTES


def get_attraction_name(bit_position):
    for attraction, index in REQUIRED_ATTRACTIONS.items():
        if index == bit_position:
            return attraction

    return None