from heapq import heappush, heappop
from typing import List, Tuple, Optional, Dict, Set

State = Tuple[int, ...]

def manhattan_distance(state: State, goal_state: State) -> int:
    """Calculates Manhattan distance heuristic."""
    total = 0
    try:
        size = int(len(state)**0.5)
        if size * size != len(state) or len(goal_state) != len(state):
             return float('inf')
        blank_tile = size * size
    except TypeError:
        return float('inf')

    goal_map = {tile: i for i, tile in enumerate(goal_state)}

    for i in range(len(state)):
        tile = state[i]
        if tile != blank_tile:
            current_row, current_col = divmod(i, size)
            goal_pos = goal_map.get(tile)

            if goal_pos is None:
                return float('inf')

            goal_row, goal_col = divmod(goal_pos, size)
            total += abs(current_row - goal_row) + abs(current_col - goal_col)
    return total

def get_neighbors_with_costs(state: State) -> List[Tuple[State, int]]:
    """Generates neighbors with single (cost 1) and double (cost 2) moves."""
    neighbors: List[Tuple[State, int]] = []
    s_list = list(state)
    try:
        size = int(len(state)**0.5)
        if size * size != len(state):
             return []
        blank_tile = size * size
        blank_index = s_list.index(blank_tile)
    except (ValueError, TypeError):
        return []

    row, col = divmod(blank_index, size)
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    single_move_intermediates: List[Tuple[State, int]] = []
    for dr, dc in moves:
        new_row, new_col = row + dr, col + dc
        if 0 <= new_row < size and 0 <= new_col < size:
            new_index = new_row * size + new_col
            new_s = s_list[:]
            new_s[blank_index], new_s[new_index] = new_s[new_index], new_s[blank_index]
            neighbor_state = tuple(new_s)
            neighbors.append((neighbor_state, 1))
            single_move_intermediates.append((neighbor_state, new_index))

    for intermediate_state, intermediate_blank_index in single_move_intermediates:
        s_intermediate = list(intermediate_state)
        row1, col1 = divmod(intermediate_blank_index, size)
        for dr, dc in moves:
            new_row2, new_col2 = row1 + dr, col1 + dc
            if 0 <= new_row2 < size and 0 <= new_col2 < size:
                new_index2 = new_row2 * size + new_col2
                if new_index2 == blank_index:
                    continue
                new_s2 = s_intermediate[:]
                new_s2[intermediate_blank_index], new_s2[new_index2] = new_s2[new_index2], new_s2[intermediate_blank_index]
                neighbor2_state = tuple(new_s2)
                neighbors.append((neighbor2_state, 2))
    return neighbors

def reconstruct_path(state: State, parent: Dict[State, Optional[State]]) -> List[State]:
    """Reconstructs the path from goal to start."""
    path: List[State] = []
    current: Optional[State] = state
    while current is not None:
        path.append(current)
        current = parent.get(current)
    path.reverse()
    return path

def solve(start_state: State, goal_state: State) -> Optional[List[State]]:
    """Solves 8-puzzle using A* with single and double moves."""
    start_state = tuple(start_state)
    goal_state = tuple(goal_state)

    n = len(start_state)
    size = int(n**0.5)
    if size * size != n or len(goal_state) != n:
         return None

    initial_h = manhattan_distance(start_state, goal_state)
    if initial_h == float('inf'):
        return None

    pq: List[Tuple[int, int, State]] = [(initial_h, 0, start_state)]
    parent: Dict[State, Optional[State]] = {start_state: None}
    g_costs: Dict[State, int] = {start_state: 0}
    closed_set: Set[State] = set()

    while pq:
        _, g_current, current_state = heappop(pq)

        if current_state in closed_set:
             continue
        closed_set.add(current_state)

        if current_state == goal_state:
            return reconstruct_path(current_state, parent)

        for next_state, move_cost in get_neighbors_with_costs(current_state):
            if next_state in closed_set:
                continue
            new_g = g_current + move_cost
            if new_g < g_costs.get(next_state, float('inf')):
                g_costs[next_state] = new_g
                parent[next_state] = current_state
                h_value = manhattan_distance(next_state, goal_state)
                if h_value == float('inf'):
                    continue
                f_new = new_g + h_value
                heappush(pq, (f_new, new_g, next_state))
    return None