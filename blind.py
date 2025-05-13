import pygame
import sys
import random
from collections import deque
import time
import copy

# --- Constants and Colors ---
DARK_BG = (18, 27, 18); PRIMARY = (52, 168, 83); PRIMARY_DARK = (39, 125, 61)
SECONDARY = (255, 255, 255); GRAY = (75, 99, 85); LIGHT_GRAY = (156, 175, 163)
TILE_BG = (30, 59, 41); TILE_SOLVED = (34, 197, 94); RED = (209, 49, 49)

# --- Animation Constants ---
SHAKE_DURATION = 200; SHAKE_MAGNITUDE = 5

# --- Target Goal States ---
TARGET_GOAL_STATES = {
    (1, 2, 3, 4, 5, 6, 7, 8, 9), (1, 4, 7, 2, 5, 8, 3, 6, 9),
    (1, 2, 3, 8, 9, 4, 7, 6, 5)}
TARGET_GOAL_LIST = list(TARGET_GOAL_STATES)

WIDTH, HEIGHT = 1280, 720

# --- Constants for Speed Slider ---
SLIDER_TRACK_HEIGHT = 12
SLIDER_HANDLE_WIDTH = 30
SLIDER_HANDLE_HEIGHT = 24
SLIDER_PUZZLE_AREA_MARGIN_TOP = 20
SLIDER_WIDTH_PERCENTAGE = 0.3
MIN_ANIMATION_SPEED = 1
MAX_ANIMATION_SPEED = 1000
DEFAULT_ANIMATION_SPEED = 400

g_switch_time = DEFAULT_ANIMATION_SPEED

# --- Helper Functions ---
def get_inversions(state):
    state_without_blank = [x for x in state if x != 9]
    inversions = 0
    for i in range(len(state_without_blank)):
        for j in range(i + 1, len(state_without_blank)):
            if state_without_blank[i] > state_without_blank[j]:
                inversions += 1
    return inversions

def is_solvable(state):
    if 9 not in state or len(state) != 9: return False
    return get_inversions(state) % 2 == 0

def apply_move(state, move_direction):
    s = list(state)
    try: blank_index = s.index(9)
    except ValueError: return None
    row, col = divmod(blank_index, 3)
    dr, dc = 0, 0
    if move_direction == 'Up': dr = -1
    elif move_direction == 'Down': dr = 1
    elif move_direction == 'Left': dc = -1
    elif move_direction == 'Right': dc = 1
    else: return None
    new_row, new_col = row + dr, col + dc
    if 0 <= new_row < 3 and 0 <= new_col < 3:
        new_index = new_row * 3 + new_col
        s[blank_index], s[new_index] = s[new_index], s[blank_index]
        return tuple(s)
    return None

def generate_specific_solvable_states(num_states, max_reverse_depth=15, required_start_value=1):
    generated_states = set()
    attempts = 0
    max_attempts = num_states * 200 # Increased attempts for robustness
    while len(generated_states) < num_states and attempts < max_attempts:
        attempts += 1
        current_state = random.choice(TARGET_GOAL_LIST)
        depth = random.randint(max(1, max_reverse_depth // 2), max_reverse_depth)
        temp_state = current_state
        move_list = ['Up', 'Down', 'Left', 'Right']
        valid_sequence = True
        for _ in range(depth):
            possible_next_states = {}
            for m in move_list:
                next_s = apply_move(temp_state, m)
                if next_s is not None: possible_next_states[m] = next_s
            if not possible_next_states: valid_sequence = False; break
            chosen_move = random.choice(list(possible_next_states.keys()))
            temp_state = possible_next_states[chosen_move]
        if not valid_sequence: continue
        if temp_state[0] == required_start_value and is_solvable(temp_state):
            generated_states.add(temp_state)
    if len(generated_states) < num_states:
        print(f"Warning: Only generated {len(generated_states)} of {num_states} states after {max_attempts} attempts.")
        # Fallback to ensure at least some states are returned if generation is difficult
        if not generated_states:
             default_s1 = (1, 2, 3, 4, 5, 9, 7, 8, 6)
             default_s2 = (1, 4, 7, 2, 5, 8, 9, 3, 6)
             if not is_solvable(default_s2) or default_s2[0] != 1: default_s2 = (1,2,3,4,9,5,7,8,6)
             defaults_to_use = []
             if is_solvable(default_s1) and default_s1[0] == required_start_value : defaults_to_use.append(default_s1)
             if is_solvable(default_s2) and default_s2[0] == required_start_value : defaults_to_use.append(default_s2)
             while len(defaults_to_use) < num_states and defaults_to_use: defaults_to_use.append(random.choice(defaults_to_use))
             if not defaults_to_use and num_states > 0: return [(1,2,3,4,5,6,7,9,8)]*num_states # Absolute fallback
             return defaults_to_use[:num_states] if num_states > 0 else []
    return list(generated_states)[:num_states]

# --- Classes ---
class AnimatedTile:
    def __init__(self, value, x, y, size):
        self.value = value; self.size = size; self.inner_size = int(size * 0.94)
        self.rect = pygame.Rect(x, y, size, size)
        self.inner_rect = pygame.Rect(0,0, self.inner_size, self.inner_size); self.inner_rect.center = self.rect.center
        self.current_x = float(x); self.current_y = float(y)
        self.target_x = float(x); self.target_y = float(y)
        self.speed = 0.25
        self.is_shaking = False; self.shake_start_time = 0
        self.shake_duration = SHAKE_DURATION; self.shake_magnitude = SHAKE_MAGNITUDE
        self.original_x_shake = float(x); self.original_y_shake = float(y)
    def set_target(self, x, y):
        if not self.is_shaking: self.target_x = float(x); self.target_y = float(y)
    def shake(self):
        if not self.is_shaking:
            self.is_shaking = True; self.shake_start_time = pygame.time.get_ticks()
            self.original_x_shake = self.current_x; self.original_y_shake = self.current_y
            self.target_x = self.current_x; self.target_y = self.current_y
    def update(self):
        now = pygame.time.get_ticks()
        if self.is_shaking:
            elapsed_shake = now - self.shake_start_time
            if elapsed_shake >= self.shake_duration:
                self.is_shaking = False; self.current_x = self.original_x_shake; self.current_y = self.original_y_shake
            else:
                offset_x = random.uniform(-self.shake_magnitude, self.shake_magnitude)
                offset_y = random.uniform(-self.shake_magnitude, self.shake_magnitude)
                self.current_x = self.original_x_shake + offset_x; self.current_y = self.original_y_shake + offset_y
        else:
            dx = self.target_x - self.current_x; dy = self.target_y - self.current_y
            if abs(dx) < 1 and abs(dy) < 1: self.current_x = self.target_x; self.current_y = self.target_y
            else: self.current_x += dx * self.speed; self.current_y += dy * self.speed
        self.rect.topleft = (int(self.current_x), int(self.current_y)); self.inner_rect.center = self.rect.center
    def draw(self, screen_param, font_param, is_in_final_goal_pos=False):
        if self.value == 9:
            if self.is_shaking: pygame.draw.rect(screen_param, RED, self.rect, border_radius=10, width=2)
            return
        bg_color = TILE_SOLVED if is_in_final_goal_pos else TILE_BG
        pygame.draw.rect(screen_param, bg_color, self.inner_rect, border_radius=10)
        text = font_param.render(str(self.value), True, SECONDARY)
        text_rect = text.get_rect(center=self.inner_rect.center); screen_param.blit(text, text_rect)
    def is_at_target(self):
        if self.is_shaking: return False
        return abs(self.current_x - self.target_x) < 1 and abs(self.current_y - self.target_y) < 1

class Button:
     def __init__(self, x, y, width, height, text, color=PRIMARY, hover_color=PRIMARY_DARK):
         self.rect = pygame.Rect(x, y, width, height); self.text = text; self.color = color
         self.hover_color = hover_color; self.is_hovered = False; self.border_radius = 8
     def draw(self, screen_param, font_param):
         current_color = self.hover_color if self.is_hovered else self.color
         pygame.draw.rect(screen_param, current_color, self.rect, border_radius=self.border_radius)
         text_surface = font_param.render(self.text, True, SECONDARY)
         text_rect = text_surface.get_rect(center=self.rect.center); screen_param.blit(text_surface, text_rect)
     def check_hover(self, mouse_pos): self.is_hovered = self.rect.collidepoint(mouse_pos); return self.is_hovered
     def is_clicked(self, mouse_pos, mouse_click): return self.is_hovered and mouse_click

class SpeedSlider:
    def __init__(self, handle_width, handle_height, track_color, handle_color, min_speed_val, max_speed_val, initial_speed_val):
        self.min_speed = min_speed_val; self.max_speed = max_speed_val; self.current_speed = initial_speed_val
        self.track_rect = pygame.Rect(0,0,0,0); self.handle_rect = pygame.Rect(0,0, handle_width, handle_height)
        self.slider_min_x = 0; self.slider_max_x = 0; self.slider_range_x = 0
        self.track_color = track_color; self.handle_color = handle_color
        self.is_dragging = False; self.active = True
    def update_layout(self, x_track_start, y_center, track_width):
        self.track_rect = pygame.Rect(x_track_start, y_center - SLIDER_TRACK_HEIGHT // 2, track_width, SLIDER_TRACK_HEIGHT)
        self.slider_min_x = self.track_rect.left + self.handle_rect.width // 2
        self.slider_max_x = self.track_rect.right - self.handle_rect.width // 2
        self.slider_range_x = self.slider_max_x - self.slider_min_x
        if self.slider_range_x <= 0: self.slider_range_x = 1
        self._update_handle_pos_from_speed()
    def _update_handle_pos_from_speed(self):
        if not self.track_rect.height: return
        percentage = (self.current_speed - self.min_speed) / (self.max_speed - self.min_speed) if self.max_speed != self.min_speed else 0.5
        handle_center_x = self.slider_min_x + percentage * self.slider_range_x
        self.handle_rect.center = (handle_center_x, self.track_rect.centery)
    def _update_speed_from_handle_pos(self):
        if self.slider_range_x == 0: return
        percentage = (self.handle_rect.centerx - self.slider_min_x) / self.slider_range_x
        self.current_speed = self.min_speed + percentage * (self.max_speed - self.min_speed)
        self.current_speed = max(self.min_speed, min(self.max_speed, self.current_speed))
    def handle_event(self, event, mouse_pos):
        global g_switch_time
        if not self.active: return False
        changed = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.handle_rect.collidepoint(mouse_pos): self.is_dragging = True; changed = True
            elif self.track_rect.collidepoint(mouse_pos):
                self.handle_rect.centerx = max(self.slider_min_x, min(mouse_pos[0], self.slider_max_x))
                self._update_speed_from_handle_pos(); g_switch_time = int(self.current_speed)
                self.is_dragging = True; changed = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_dragging: self.is_dragging = False; changed = True
        elif event.type == pygame.MOUSEMOTION and self.is_dragging:
            self.handle_rect.centerx = max(self.slider_min_x, min(mouse_pos[0], self.slider_max_x))
            self._update_speed_from_handle_pos(); g_switch_time = int(self.current_speed)
            changed = True
        return changed
    def draw(self, screen_param, font_param):
        if not self.active or not self.track_rect.width: return
        pygame.draw.rect(screen_param, self.track_color, self.track_rect, border_radius=SLIDER_TRACK_HEIGHT // 2)
        pygame.draw.rect(screen_param, self.handle_color, self.handle_rect, border_radius=5)
        speed_text = f"Tốc độ: {int(self.current_speed)}ms"
        text_surf = font_param.render(speed_text, True, LIGHT_GRAY)
        text_rect = text_surf.get_rect(midleft=(self.track_rect.right + 15, self.track_rect.centery)); screen_param.blit(text_surf, text_rect)
        fast_label = font_param.render("Nhanh", True, LIGHT_GRAY)
        screen_param.blit(fast_label, fast_label.get_rect(midright=(self.track_rect.left - 10, self.track_rect.centery)))
    def get_speed(self): return int(self.current_speed)

# --- Blind Search Algorithm ---
def find_common_path(initial_belief_states, target_goals_set):
    if not initial_belief_states: return None
    initial_belief_tuple = tuple(sorted(initial_belief_states))
    if all(state in target_goals_set for state in initial_belief_tuple): return []
    queue = deque([(initial_belief_tuple, [])]); visited = {initial_belief_tuple}
    move_directions = ['Up', 'Down', 'Left', 'Right']
    max_iterations = 200000; iterations = 0 # Adjust max_iterations if needed
    # print(f"Blind Search: Starting BFS with {len(initial_belief_states)} initial states.")
    while queue:
        iterations += 1
        if iterations > max_iterations:
            print(f"Blind Search BFS: Max iterations ({max_iterations}) reached for current attempt.")
            return None
        current_belief_tuple, current_path = queue.popleft()
        for move in move_directions:
            next_belief_list = []
            for state in current_belief_tuple:
                next_state = apply_move(state, move)
                next_belief_list.append(next_state if next_state is not None else state)
            next_belief_tuple = tuple(sorted(next_belief_list))
            if next_belief_tuple not in visited:
                 if all(state in target_goals_set for state in next_belief_tuple):
                     print(f"Blind Search BFS: Path found in {len(current_path) + 1} moves, {iterations} iterations.")
                     return current_path + [move]
                 visited.add(next_belief_tuple)
                 queue.append((next_belief_tuple, current_path + [move]))
    # print(f"Blind Search BFS: Queue exhausted after {iterations} iterations, no path found for current attempt.")
    return None

# --- GUI Function ---
def draw_info_box_blind(screen_param, font_obj, info_font_obj, path_length_param, current_step_param,
                        total_steps_param, current_move_str_param, box_rect_param):
    pygame.draw.rect(screen_param, GRAY, box_rect_param, border_radius=10)
    pygame.draw.rect(screen_param, DARK_BG, box_rect_param.inflate(-4, -4), border_radius=10)
    title_surface = font_obj.render("Thông tin Giải Mù", True, SECONDARY)
    title_rect = title_surface.get_rect(centerx=box_rect_param.centerx, y=box_rect_param.y + 20); screen_param.blit(title_surface, title_rect)
    info_lines = [
        f"Thuật toán: Blind Belief Search",
        f"Độ dài đường đi: {path_length_param if path_length_param is not None else 'N/A'}",
        f"Bước hiện tại: {current_step_param + 1 if path_length_param is not None else 'N/A'}/{total_steps_param if total_steps_param is not None else 'N/A'}",
        f"Di chuyển: {current_move_str_param if current_move_str_param else '---'}"
    ]
    line_y = box_rect_param.y + 60
    for text in info_lines:
        line_surf = info_font_obj.render(text, True, LIGHT_GRAY)
        screen_param.blit(line_surf, (box_rect_param.x + 20, line_y)); line_y += 30
    if total_steps_param is not None and total_steps_param > 0:
        progress_rect_bg = pygame.Rect(box_rect_param.x + 20, box_rect_param.bottom - 60, box_rect_param.width - 40, 20)
        pygame.draw.rect(screen_param, GRAY, progress_rect_bg, border_radius=10)
        progress_ratio = min(1.0, max(0.0, (current_step_param + 1) / total_steps_param if path_length_param is not None else 0))
        progress_width = int(progress_ratio * progress_rect_bg.width)
        if progress_width > 0:
            progress_rect_fg = pygame.Rect(progress_rect_bg.x, progress_rect_bg.y, progress_width, progress_rect_bg.height)
            pygame.draw.rect(screen_param, PRIMARY, progress_rect_fg, border_radius=10)

def update_single_puzzle_tiles(puzzle_tiles_param, new_state_tuple_param, puzzle_layout_param):
    value_pos_map = {val: i for i, val in enumerate(new_state_tuple_param)}
    for tile_obj in puzzle_tiles_param:
        if tile_obj.value in value_pos_map:
            new_index = value_pos_map[tile_obj.value]
            row, col = divmod(new_index, 3)
            target_x = puzzle_layout_param["x"] + col * puzzle_layout_param["tile_size"]
            target_y = puzzle_layout_param["y"] + row * puzzle_layout_param["tile_size"]
            tile_obj.set_target(target_x, target_y)

def run_blind_search(main_font, main_title_font, main_puzzle_font, main_info_font, main_button_font):
    global WIDTH, HEIGHT, g_switch_time, screen
    font = main_font; title_font = main_title_font; puzzle_font = main_puzzle_font
    info_font = main_info_font; button_font = main_button_font

    if not pygame.get_init(): pygame.init()
    try:
        screen = pygame.display.get_surface()
        if screen is None:
            screen_info_pyg = pygame.display.Info()
            WIDTH, HEIGHT = screen_info_pyg.current_w, screen_info_pyg.current_h
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.SRCALPHA)
        else: WIDTH, HEIGHT = screen.get_size()
        pygame.display.set_caption("Blind Search - 8 Puzzle")
    except pygame.error as e:
        print(f"Screen setup error in blind.py: {e}. Using fallback {WIDTH}x{HEIGHT}.")
        screen = pygame.display.set_mode((WIDTH, HEIGHT)); pygame.display.set_caption("Blind Search - 8 Puzzle")

    clock = pygame.time.Clock()
    
    # --- UI Elements (Buttons, Slider) ---
    speed_slider = SpeedSlider(SLIDER_HANDLE_WIDTH, SLIDER_HANDLE_HEIGHT, GRAY, PRIMARY,
                               MIN_ANIMATION_SPEED, MAX_ANIMATION_SPEED, g_switch_time)
    button_width_val, button_height_val = 120, 40; bottom_button_y_val = HEIGHT - 70
    total_buttons_width = 4 * button_width_val + 3 * 20
    buttons_start_x_val = (WIDTH - total_buttons_width) / 2
    auto_btn = Button(buttons_start_x_val, bottom_button_y_val, button_width_val, button_height_val, "Auto: On")
    next_btn = Button(auto_btn.rect.right + 20, bottom_button_y_val, button_width_val, button_height_val, "Tiếp theo")
    reset_btn = Button(next_btn.rect.right + 20, bottom_button_y_val, button_width_val, button_height_val, "Làm lại")
    back_menu_btn = Button(reset_btn.rect.right + 20, bottom_button_y_val, button_width_val, button_height_val, "Quay lại Menu")
    
    slider_track_w_val = WIDTH * SLIDER_WIDTH_PERCENTAGE; slider_center_x_val = WIDTH * 0.4
    slider_track_start_x_val = slider_center_x_val - slider_track_w_val / 2
    slider_y_center_val = SLIDER_PUZZLE_AREA_MARGIN_TOP + SLIDER_HANDLE_HEIGHT / 2 + 60
    speed_slider.update_layout(slider_track_start_x_val, slider_y_center_val, slider_track_w_val)
    
    info_box_w_val = min(WIDTH * 0.25, 350); info_box_h_val = 250
    info_box_x_val = WIDTH - info_box_w_val - 30
    # Define puzzle_start_y_val before it's used for info_box_y_val
    # This will be set properly after path is found and puzzles are laid out
    puzzle_start_y_val_for_info_box = SLIDER_PUZZLE_AREA_MARGIN_TOP + SLIDER_HANDLE_HEIGHT + 80 # Estimate
    info_box_y_val = puzzle_start_y_val_for_info_box
    info_box_rect = pygame.Rect(info_box_x_val, info_box_y_val, info_box_w_val, info_box_h_val)

    # --- Path Finding Loop with Retries ---
    common_path = None; initial_states = []
    all_animating_puzzles = []; current_animated_state_tuples = []; puzzle_layout_infos = []
    ui_state = "searching"; message_display = "Đang tìm kiếm cấu hình và đường đi..."
    attempt_count = 0

    keep_searching_for_path = True
    while keep_searching_for_path:
        attempt_count += 1
        print(f"Blind Search: Attempt {attempt_count} to find path.")
        for event_search in pygame.event.get(): # Allow quitting during search
            if event_search.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event_search.type == pygame.KEYDOWN and event_search.key == pygame.K_ESCAPE: return

        screen.fill(DARK_BG)
        title_surf_main_search = title_font.render("Tìm kiếm mù - Demo", True, SECONDARY)
        screen.blit(title_surf_main_search, title_surf_main_search.get_rect(centerx=WIDTH // 2, y=SLIDER_PUZZLE_AREA_MARGIN_TOP))
        current_search_msg = message_display if attempt_count == 1 else f"{message_display} (Thử lại lần {attempt_count-1})"
        search_msg_surf = font.render(current_search_msg, True, LIGHT_GRAY)
        screen.blit(search_msg_surf, search_msg_surf.get_rect(centerx=WIDTH//2, y=HEIGHT//2))
        pygame.display.flip()

        num_initial_states_to_gen = 2 # Can be configured
        initial_states_temp = generate_specific_solvable_states(num_initial_states_to_gen, 12, 1)

        if not initial_states_temp or len(initial_states_temp) < num_initial_states_to_gen:
            message_display = "Lỗi tạo trạng thái. Đang thử lại..."
            print("Blind Search: Failed to generate enough initial states. Retrying state generation...")
            time.sleep(0.5) # Brief pause before retrying state generation
            continue # Retry generating states

        initial_states = initial_states_temp
        print(f"Blind Search: Generated {len(initial_states)} states. Finding common path...")
        
        common_path_temp = find_common_path(initial_states, TARGET_GOAL_STATES)

        if common_path_temp is not None:
            common_path = common_path_temp
            keep_searching_for_path = False # Path found, exit loop

            # --- Setup for animation (now that path is found) ---
            current_animated_state_tuples = list(initial_states)
            num_puzzles_val = len(initial_states)
            puzzle_display_area_width = WIDTH * 0.6
            available_width_per_puzzle = (puzzle_display_area_width - (num_puzzles_val + 1) * 20) / num_puzzles_val if num_puzzles_val > 0 else 0
            available_height_for_puzzles = HEIGHT * 0.5
            anim_tile_size_val = min(available_width_per_puzzle / 3, available_height_for_puzzles / 3) * 0.9 if available_width_per_puzzle > 0 else 50
            anim_puzzle_actual_width = anim_tile_size_val * 3
            total_puzzles_block_width = num_puzzles_val * anim_puzzle_actual_width + (num_puzzles_val - 1) * 20
            puzzle_block_start_x = 20 + (puzzle_display_area_width - total_puzzles_block_width) / 2
            puzzle_start_y_val = SLIDER_PUZZLE_AREA_MARGIN_TOP + SLIDER_HANDLE_HEIGHT + 80
            
            info_box_y_val = puzzle_start_y_val # Update info_box_y based on actual puzzle layout
            info_box_rect.y = info_box_y_val

            all_animating_puzzles.clear(); puzzle_layout_infos.clear() # Ensure clean lists
            for i, init_state in enumerate(initial_states):
                px = puzzle_block_start_x + i * (anim_puzzle_actual_width + 20)
                py = puzzle_start_y_val
                puzzle_layout_infos.append({"x": px, "y": py, "tile_size": anim_tile_size_val})
                current_puzzle_tiles = []
                for idx, val in enumerate(init_state):
                    r, c = divmod(idx, 3)
                    tile_x = px + c * anim_tile_size_val; tile_y = py + r * anim_tile_size_val
                    tile = AnimatedTile(val, tile_x, tile_y, anim_tile_size_val)
                    current_puzzle_tiles.append(tile)
                all_animating_puzzles.append(current_puzzle_tiles)
            
            if not common_path:
                message_display = "Các trạng thái đã ở đích. Sẵn sàng."
                ui_state = "finished"
            else:
                message_display = f"Tìm thấy đường đi chung: {len(common_path)} bước."
                ui_state = "animating"
        else: # common_path_temp is None
            message_display = "Không tìm thấy đường đi chung. Đang thử lại..."
            print("Blind Search: No common path found. Retrying path search...")
            time.sleep(0.5) # Brief pause before retrying path search
            # Loop continues to retry path finding

    # --- Main Animation Loop ---
    current_move_index = 0; last_anim_update_time = pygame.time.get_ticks(); auto_mode = True
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos(); mouse_click = False; now_time = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: mouse_click = True
            if ui_state == "animating" or ui_state == "finished": speed_slider.handle_event(event, mouse_pos)
        
        if mouse_click:
            if back_menu_btn.is_clicked(mouse_pos, True): running = False
            if ui_state == "animating" or ui_state == "finished":
                if auto_btn.is_clicked(mouse_pos, True):
                    auto_mode = not auto_mode; auto_btn.text = "Auto: On" if auto_mode else "Auto: Off"
                elif reset_btn.is_clicked(mouse_pos, True) and initial_states: # Ensure initial_states is populated
                    current_move_index = 0
                    current_animated_state_tuples = list(initial_states)
                    for i, p_tiles in enumerate(all_animating_puzzles):
                        if i < len(initial_states) and i < len(puzzle_layout_infos):
                            update_single_puzzle_tiles(p_tiles, initial_states[i], puzzle_layout_infos[i])
                    last_anim_update_time = now_time
                    ui_state = "finished" if not common_path else "animating"
                    message_display = f"Đã reset. Đường đi: {len(common_path) if common_path else 0} bước."

        if ui_state == "animating" and common_path:
            all_tiles_settled = all(tile.is_at_target() for p_tiles in all_animating_puzzles for tile in p_tiles)
            if current_move_index < len(common_path):
                process_next_step = False
                if auto_mode and all_tiles_settled and (now_time - last_anim_update_time >= g_switch_time): process_next_step = True
                elif not auto_mode and next_btn.is_clicked(mouse_pos, mouse_click) and all_tiles_settled: process_next_step = True; mouse_click = False
                
                if process_next_step:
                    move_to_apply = common_path[current_move_index]
                    for i_puzzle in range(len(current_animated_state_tuples)):
                        current_s = current_animated_state_tuples[i_puzzle]
                        p_tiles = all_animating_puzzles[i_puzzle]
                        next_s = apply_move(current_s, move_to_apply)
                        if next_s:
                            current_animated_state_tuples[i_puzzle] = next_s
                            update_single_puzzle_tiles(p_tiles, next_s, puzzle_layout_infos[i_puzzle])
                        else: # Invalid move for this specific puzzle (should ideally not happen with a common path logic)
                            blank_tile = next((t for t in p_tiles if t.value == 9), None)
                            if blank_tile: blank_tile.shake()
                    current_move_index += 1; last_anim_update_time = now_time
            elif all_tiles_settled:
                ui_state = "finished"; message_display = f"Hoàn thành ({len(common_path)} bước)"
                if not all(s in TARGET_GOAL_STATES for s in current_animated_state_tuples):
                    message_display += " (Lỗi trạng thái đích!)"; print("Error: Some puzzles not in target goal.")

        for p_tiles in all_animating_puzzles:
            for tile in p_tiles: tile.update()

        screen.fill(DARK_BG)
        title_surf_main_anim = title_font.render("Tìm kiếm mù - Demo", True, SECONDARY)
        screen.blit(title_surf_main_anim, title_surf_main_anim.get_rect(centerx=WIDTH // 2, y=SLIDER_PUZZLE_AREA_MARGIN_TOP))
        if ui_state != "searching": speed_slider.draw(screen, button_font)
        
        for i_draw, p_tiles in enumerate(all_animating_puzzles):
            is_final = ui_state == "finished" and i_draw < len(current_animated_state_tuples) and current_animated_state_tuples[i_draw] in TARGET_GOAL_STATES
            for tile in p_tiles:
                tile_in_goal_pos = False
                if is_final and i_draw < len(current_animated_state_tuples):
                    s_list = list(current_animated_state_tuples[i_draw])
                    try:
                        tile_idx = s_list.index(tile.value)
                        tile_in_goal_pos = any(tile.value == goal[tile_idx] for goal in TARGET_GOAL_LIST)
                    except ValueError: pass
                tile.draw(screen, puzzle_font, tile_in_goal_pos)
        
        path_len_disp = len(common_path) if common_path else 0
        curr_step_disp = current_move_index -1
        total_steps_disp = path_len_disp
        curr_move_str = "---"
        if common_path and current_move_index > 0 and current_move_index <= path_len_disp : curr_move_str = common_path[current_move_index -1]
        elif ui_state == "finished": curr_move_str = "Hoàn thành!" if path_len_disp > 0 else "Đã ở đích"; curr_step_disp = path_len_disp -1 if path_len_disp > 0 else 0
        
        draw_info_box_blind(screen, font, info_font, path_len_disp, curr_step_disp, total_steps_disp, curr_move_str, info_box_rect)
        for btn in [auto_btn, next_btn, reset_btn, back_menu_btn]: btn.check_hover(mouse_pos); btn.draw(screen, button_font)
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    pygame.init(); pygame.font.init()
    fb_font, fb_title_font, fb_puzzle_font, fb_info_font, fb_button_font = None,None,None,None,None
    try:
        fb_font_name = "Arial"
        if pygame.font.match_font(fb_font_name) is None: fb_font_name = pygame.font.get_default_font()
        fb_font = pygame.font.SysFont(fb_font_name, 22); fb_title_font = pygame.font.SysFont(fb_font_name, 36, bold=True)
        fb_puzzle_font = pygame.font.SysFont(fb_font_name, 50, bold=True); fb_info_font = pygame.font.SysFont(fb_font_name, 20)
        fb_button_font = pygame.font.SysFont(fb_font_name, 20)
        print(f"Standalone blind.py: Using font {fb_font_name}")
    except Exception as e:
        print(f"Standalone blind.py font error: {e}. Using Pygame default.")
        fb_font = pygame.font.Font(None, 24); fb_title_font = pygame.font.Font(None, 36)
        fb_puzzle_font = pygame.font.Font(None, 50); fb_info_font = pygame.font.Font(None, 22)
        fb_button_font = pygame.font.Font(None, 20)
    run_blind_search(fb_font, fb_title_font, fb_puzzle_font, fb_info_font, fb_button_font)
    pygame.quit(); sys.exit()