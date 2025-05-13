def get_neighbors(state):
    neighbors = []
    s = list(state)
    blank_index = s.index(9)
    row, col = divmod(blank_index, 3)
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    for dr, dc in moves:
        new_row = row + dr
        new_col = col + dc
        if 0 <= new_row < 3 and 0 <= new_col < 3:
            new_index = new_row * 3 + new_col
            new_s = s[:]
            new_s[blank_index], new_s[new_index] = new_s[new_index], new_s[blank_index]
            neighbors.append(tuple(new_s))
    return neighbors

def reconstruct_path(state, parent):
    path = []
    while state is not None:
        path.append(state)
        state = parent[state]
    path.reverse()
    return path

def solve(start_state, goal_state):
    """Solves the 8-puzzle using Depth-First Search."""
    stack = [start_state]
    visited = set([start_state])
    parent = {start_state: None}
    
    while stack:
        current = stack.pop()
        if current == goal_state:
            return reconstruct_path(current, parent)
        # For DFS, neighbors are typically added in a specific order or reversed
        # to mimic recursive behavior if desired. Here, simple order.
        for next_state in get_neighbors(current): 
            if next_state not in visited:
                visited.add(next_state)
                parent[next_state] = current
                stack.append(next_state)
    return None