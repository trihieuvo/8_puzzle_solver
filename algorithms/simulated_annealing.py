import random
import math

def solve(start, goal, initial_temperature=100, cooling_rate=0.003):
    """Solves 8-Puzzle using Simulated Annealing."""
    def get_neighbors(state):
        empty_index = state.index(9); row, col = divmod(empty_index, 3); neighbors = []
        moves = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for dr, dc in moves:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < 3 and 0 <= new_col < 3:
                new_index = new_row * 3 + new_col; new_state = list(state)
                new_state[empty_index], new_state[new_index] = new_state[new_index], new_state[empty_index]
                neighbors.append(tuple(new_state))
        return neighbors

    def heuristic(state):
        distance = 0
        for i in range(9):
            if state[i] != 9:
                goal_index = goal.index(state[i]); row1, col1 = i // 3, i % 3
                row2, col2 = goal_index // 3, goal_index % 3
                distance += abs(row1 - row2) + abs(col1 - col2)
        return distance

    current_state = start; path = [current_state]
    current_heuristic = heuristic(current_state)
    temperature = initial_temperature; iterations = 0; max_iterations = 50000 # Added max_iterations

    while current_state != goal and iterations < max_iterations : # Added iteration check
        iterations +=1
        if temperature <= 0.0001: return None # Stop if too cold

        neighbors = get_neighbors(current_state)
        if not neighbors: return None # Stuck

        next_state = random.choice(neighbors)
        next_heuristic = heuristic(next_state)
        delta_e = next_heuristic - current_heuristic

        if delta_e < 0 or random.random() < math.exp(-delta_e / temperature):
            current_state = next_state
            path.append(current_state) # Path tracks the sequence of accepted states
            current_heuristic = next_heuristic
        temperature *= (1 - cooling_rate)
    
    return path if current_state == goal else None # Return path only if goal is reached