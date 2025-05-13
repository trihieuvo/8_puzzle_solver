from collections import deque
from typing import List, Tuple, Optional, Set, Dict

State = Tuple[int, ...]

# --- Dán hàm get_neighbors_with_double_moves vào đây ---
def get_neighbors_with_double_moves(state: State) -> List[State]:
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



def reconstruct_path(state: State, parent: Dict[State, Optional[State]]) -> List[State]:

    path: List[State] = []
    current: Optional[State] = state
    while current is not None:
        path.append(current)
        current = parent.get(current)
    path.reverse()
    return path

# Hàm Depth-Limited Search (DLS) - Phiên bản lặp (không đệ quy)
def depth_limited_search(start_state: State, goal_state: State, depth_limit: int) -> Optional[List[State]]:
    """
    Thực hiện DLS lặp, trả về đường đi nếu tìm thấy trong giới hạn độ sâu.
    """
    # Stack lưu (state, path_list_to_state)
    stack: List[Tuple[State, List[State]]] = [(start_state, [start_state])]
    # Visited set để tránh chu trình TRONG một lần DLS ở độ sâu cụ thể
    visited_at_depth: Dict[State, int] = {start_state: 0} # Lưu state và độ sâu nhỏ nhất tìm thấy nó

    while stack:
        current_state, current_path = stack.pop()
        current_depth = len(current_path) - 1

        if current_state == goal_state:
            return current_path 

        if current_depth >= depth_limit:
            continue 
        neighbors = get_neighbors_with_double_moves(current_state)
        for next_state in reversed(neighbors):
            new_depth = current_depth + 1
            if next_state not in visited_at_depth or new_depth < visited_at_depth[next_state]:
                 visited_at_depth[next_state] = new_depth
                 new_path = current_path + [next_state]
                 stack.append((next_state, new_path))

    return None 

def solve(start_state: State, goal_state: State, max_depth: int = 30) -> Optional[List[State]]:
    
    start_state = tuple(start_state)
    goal_state = tuple(goal_state)

    if start_state == goal_state:
        return [start_state]
    for depth in range(max_depth + 1):
        result_path = depth_limited_search(start_state, goal_state, depth)
        if result_path:
            return result_path
    return None

