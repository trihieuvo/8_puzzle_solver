import random
from typing import List, Tuple, Optional, Set, Dict

State = Tuple[int, ...]

def manhattan_distance(state: State, goal_state: State) -> int:
    """Calculates Manhattan distance heuristic."""
    total = 0
    try:
        size = int(len(state)**0.5)
        if size * size != len(state) or len(goal_state) != len(state): return float('inf')
        blank_tile = size * size
        goal_map = {tile: i for i, tile in enumerate(goal_state)}
    except (ValueError, TypeError): return float('inf')

    for i in range(len(state)):
        tile = state[i]
        if tile != blank_tile:
            curr_row, curr_col = divmod(i, size)
            goal_pos = goal_map.get(tile)
            if goal_pos is None: return float('inf')
            goal_row, goal_col = divmod(goal_pos, size)
            total += abs(curr_row - goal_row) + abs(curr_col - goal_col)
    return total

def get_neighbors_with_double_moves(state: State) -> List[State]:
    """Generates neighbors with single and double moves, returns unique states."""
    neighbors: Set[State] = set(); s_list = list(state)
    try:
        size = int(len(state)**0.5);
        if size * size != len(state): return []
        blank_tile = size * size; blank_index = s_list.index(blank_tile)
    except (ValueError, TypeError): return []
    row, col = divmod(blank_index, size); moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    single_move_intermediates: List[Tuple[State, int]] = []
    for dr, dc in moves:
        new_row, new_col = row + dr, col + dc
        if 0 <= new_row < size and 0 <= new_col < size:
            new_index = new_row * size + new_col; new_s = s_list[:]; new_s[blank_index], new_s[new_index] = new_s[new_index], new_s[blank_index]
            neighbor_state = tuple(new_s); neighbors.add(neighbor_state); single_move_intermediates.append((neighbor_state, new_index))
    for intermediate_state, intermediate_blank_index in single_move_intermediates:
        s_intermediate = list(intermediate_state); row1, col1 = divmod(intermediate_blank_index, size)
        for dr, dc in moves:
            new_row2, new_col2 = row1 + dr, col1 + dc
            if 0 <= new_row2 < size and 0 <= new_col2 < size:
                new_index2 = new_row2 * size + new_col2
                if new_index2 == blank_index: continue
                new_s2 = s_intermediate[:]; new_s2[intermediate_blank_index], new_s2[new_index2] = new_s2[new_index2], new_s2[intermediate_blank_index]
                neighbor2_state = tuple(new_s2); neighbors.add(neighbor2_state)
    return list(neighbors)

def is_solvable(state, goal_state=(1, 2, 3, 4, 5, 6, 7, 8, 9)):
    """Checks if a 3x3 puzzle state is solvable relative to a goal."""
    try:
        state_list = [x for x in state if x != 9]; goal_list = [x for x in goal_state if x != 9]
        if len(state_list) != 8 or len(goal_list) != 8: return False
        inversions = 0
        for i in range(len(state_list)):
            for j in range(i + 1, len(state_list)):
                if state_list[i] > state_list[j]: inversions += 1
        goal_inversions = 0
        for i in range(len(goal_list)):
            for j in range(i + 1, len(goal_list)):
                if goal_list[i] > goal_list[j]: goal_inversions += 1
        return (inversions % 2) == (goal_inversions % 2)
    except: return False

def solve(start_state: State, goal_state: State, max_iterations=1000, max_restarts=50) -> Optional[List[State]]:
    """Solves 8-puzzle using Hill Climbing with double moves and random restarts."""
    start_state = tuple(start_state)
    goal_state = tuple(goal_state)

    if not is_solvable(start_state, goal_state):
        return None

    best_state_overall = start_state
    best_score_overall = manhattan_distance(start_state, goal_state)
    overall_path = []

    for restart in range(max_restarts):
        current_state = start_state
        if restart > 0:
            if random.random() < 0.7 and best_state_overall != start_state:
                 current_state = best_state_overall

        current_score = manhattan_distance(current_state, goal_state)
        path = [current_state]
        local_visited = {current_state}

        iterations = 0
        stuck_counter = 0
        while current_state != goal_state and iterations < max_iterations:
            iterations += 1
            neighbors = get_neighbors_with_double_moves(current_state)
            best_neighbor = None
            best_neighbor_score = current_score
            
            candidates = []
            for neighbor in neighbors:
                 if neighbor not in local_visited:
                      score = manhattan_distance(neighbor, goal_state)
                      if score < best_neighbor_score:
                           candidates.append((neighbor, score))
            if candidates:
                 candidates.sort(key=lambda x: x[1]) # For simple hill climbing, could just pick first or random from better
                 best_neighbor, best_neighbor_score = random.choice(candidates) if candidates else (None, current_score) # More stochastic if multiple equally good
                 stuck_counter = 0
            else:
                 stuck_counter += 1
                 if stuck_counter >= 5:
                      break
                 unvisited_neighbors = [n for n in neighbors if n not in local_visited]
                 if unvisited_neighbors:
                     best_neighbor = random.choice(unvisited_neighbors)
                     best_neighbor_score = manhattan_distance(best_neighbor, goal_state)
                 else:
                     break
            
            if best_neighbor is None: break
            current_state = best_neighbor
            current_score = best_neighbor_score
            path.append(current_state)
            local_visited.add(current_state)

            if current_score < best_score_overall:
                best_state_overall = current_state
                best_score_overall = current_score
            if current_state == goal_state:
                return path
        
        if path and (not overall_path or manhattan_distance(path[-1], goal_state) < manhattan_distance(overall_path[-1], goal_state)):
            overall_path = path
            
    if best_score_overall == 0 and overall_path and overall_path[-1] == goal_state:
        return overall_path
    return None if not (overall_path and overall_path[-1] == goal_state) else overall_path