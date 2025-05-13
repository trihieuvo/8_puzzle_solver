import pygame
import sys
import threading
import time
import math
import random
from collections import deque
import traceback

# --- Constants and Colors ---
DARK_BG = (18, 27, 18)
PRIMARY = (52, 168, 83)
PRIMARY_DARK = (39, 125, 61)
SECONDARY = (255, 255, 255)
GRAY = (75, 99, 85)
LIGHT_GRAY = (156, 175, 163)
TILE_BG = (30, 59, 41)
TILE_EMPTY_BG = GRAY
RED = (209, 49, 49)
YELLOW = (240, 180, 0)
TILE_SOLVED = (34, 197, 94)

# --- Global Variables for fill.py ---
WIDTH, HEIGHT = 0, 0
screen = None
clock = None
font = None
title_font = None
puzzle_font = None
button_font = None
info_font = None

EMPTY_SLOT = 0 # Represents an empty slot in the puzzle grid

# --- Helper Functions ---
def is_valid_puzzle_state(state):
    """Checks if state is a valid permutation of 1-9."""
    return isinstance(state, (list, tuple)) and len(state) == 9 and sorted(state) == list(range(1, 10))

# --- Classes ---
class Button:
     def __init__(self, x, y, width, height, text, color=PRIMARY, hover_color=PRIMARY_DARK):
         self.rect = pygame.Rect(x, y, width, height); self.text = text; self.color = color
         self.hover_color = hover_color; self.is_hovered = False; self.border_radius = 8
     def draw(self, screen_param, font_param):
         color = self.hover_color if self.is_hovered else self.color
         pygame.draw.rect(screen_param, color, self.rect, border_radius=self.border_radius)
         text_surface = font_param.render(self.text, True, SECONDARY); text_rect = text_surface.get_rect(center=self.rect.center); screen_param.blit(text_surface, text_rect)
     def check_hover(self, mouse_pos): self.is_hovered = self.rect.collidepoint(mouse_pos); return self.is_hovered
     def is_clicked(self, mouse_pos, mouse_click): return self.is_hovered and mouse_click

class MessageBox:
    def __init__(self, width, height, title, message, button_text="OK"):
        self.rect = pygame.Rect((WIDTH - width) // 2, (HEIGHT - height) // 2, width, height)
        self.title = title; self.message = message; self.border_radius = 10; self.active = False
        button_width = 100; button_height_val = 40
        button_x = self.rect.x + (self.rect.width - button_width) // 2
        button_y = self.rect.bottom - button_height_val - 20
        self.ok_button = Button(button_x, button_y, button_width, button_height_val, button_text)
    def draw(self, screen_param, title_font_param, font_param, button_font_param):
        if not self.active: return
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA); overlay.fill((0, 0, 0, 128)); screen_param.blit(overlay, (0, 0))
        pygame.draw.rect(screen_param, GRAY, self.rect, border_radius=self.border_radius)
        pygame.draw.rect(screen_param, DARK_BG, self.rect.inflate(-4, -4), border_radius=self.border_radius)
        title_surface = title_font_param.render(self.title, True, SECONDARY); title_rect = title_surface.get_rect(centerx=self.rect.centerx, y=self.rect.y + 20); screen_param.blit(title_surface, title_rect)
        lines = self.message.split('\n'); start_y = self.rect.y + 70
        for i, line in enumerate(lines): msg_surf = font_param.render(line, True, LIGHT_GRAY); msg_rect = msg_surf.get_rect(centerx=self.rect.centerx, y=start_y + i * 30); screen_param.blit(msg_surf, msg_rect)
        self.ok_button.draw(screen_param, button_font_param)
    def check_hover(self, mouse_pos):
        if not self.active: return False
        return self.ok_button.check_hover(mouse_pos)
    def handle_event(self, event):
        if not self.active: return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.ok_button.is_clicked(event.pos, True): self.active = False; return True
        return False

class AnimatedNumberTile:
    def __init__(self, value, x, y, size):
        self.value = value
        self.target_value = value
        self.size = size
        self.inner_size = int(size * 0.94)
        self.rect = pygame.Rect(x, y, size, size)
        self.inner_rect = pygame.Rect(0, 0, self.inner_size, self.inner_size)
        self.inner_rect.center = self.rect.center
        self.is_appearing = False
        self.appear_start_time = 0
        self.appear_duration = 0.4
        self.current_scale = 1.0
        self.current_y_offset = 0
        self.highlight = False

    def set_value(self, new_value, trigger_animation=False):
        if new_value != self.value:
            self.target_value = new_value
            if trigger_animation and new_value != EMPTY_SLOT:
                self.is_appearing = True
                self.appear_start_time = time.time()
                self.current_scale = 1.5
                self.current_y_offset = -self.size * 0.2
                self.highlight = True
            else:
                self.value = new_value
                self.is_appearing = False
                self.highlight = new_value != EMPTY_SLOT
        else:
             self.highlight = False

    def update(self):
        if self.is_appearing:
            elapsed = time.time() - self.appear_start_time
            if elapsed >= self.appear_duration:
                self.is_appearing = False
                self.value = self.target_value
                self.current_scale = 1.0
                self.current_y_offset = 0
            else:
                progress = elapsed / self.appear_duration
                ease_out_factor = 1.0 - (1.0 - progress) ** 3
                self.current_scale = 1.0 + 0.5 * (1.0 - ease_out_factor)
                self.current_y_offset = -self.size * 0.2 * (1.0 - ease_out_factor)
                self.value = self.target_value

    def draw(self, screen_param, font_param):
        draw_rect = self.inner_rect.copy()
        scaled_size = int(self.inner_size * self.current_scale)
        draw_rect.width = scaled_size
        draw_rect.height = scaled_size
        draw_rect.centerx = self.inner_rect.centerx
        draw_rect.centery = self.inner_rect.centery + int(self.current_y_offset)
        bg_color = TILE_EMPTY_BG if self.value == EMPTY_SLOT else TILE_BG
        if self.highlight and not self.is_appearing:
             bg_color = YELLOW
        pygame.draw.rect(screen_param, bg_color, draw_rect, border_radius=int(10 * self.current_scale))
        if self.value != EMPTY_SLOT:
            scaled_font_size = int(font_param.get_height() * self.current_scale * 1.1)
            try: scaled_font = pygame.font.SysFont(font_param.get_name(), scaled_font_size, bold=True)
            except: scaled_font = pygame.font.Font(None, scaled_font_size)
            text = scaled_font.render(str(self.value), True, SECONDARY)
            text_rect = text.get_rect(center=draw_rect.center)
            screen_param.blit(text, text_rect)
        if self.highlight and self.is_appearing:
             pygame.draw.rect(screen_param, YELLOW, draw_rect, border_radius=int(10 * self.current_scale), width=3)

# --- Backtracking Logic ---
animation_path = []
backtrack_target_state = []
backtrack_thread = None
backtrack_running = False
backtrack_finished = False
backtrack_success = False

def backtrack_fill_recursive(index, current_grid_state, used_numbers):
    global animation_path, backtrack_target_state, backtrack_running
    if not backtrack_running: return False
    if index == 9:
        return list(current_grid_state) == list(backtrack_target_state)
    correct_num = backtrack_target_state[index]
    if correct_num in used_numbers:
        print(f"Fill Error: Number {correct_num} already used at index {index}. Target state may be invalid.")
        return False
    current_grid_state[index] = correct_num
    used_numbers.add(correct_num)
    animation_path.append(list(current_grid_state))
    found = backtrack_fill_recursive(index + 1, current_grid_state, used_numbers)
    if found:
        return True
    if backtrack_running:
        used_numbers.remove(correct_num)
        current_grid_state[index] = EMPTY_SLOT
        animation_path.append(list(current_grid_state))
    return False

def run_backtracking_thread(target_state_param):
    global animation_path, backtrack_target_state, backtrack_running, backtrack_finished, backtrack_success
    backtrack_target_state = target_state_param
    backtrack_running = True
    backtrack_finished = False
    backtrack_success = False
    animation_path.clear()
    initial_grid = [EMPTY_SLOT] * 9
    used = set()
    animation_path.append(list(initial_grid))
    try:
        backtrack_success = backtrack_fill_recursive(0, initial_grid, used)
    except Exception as e:
        print(f"Error in backtracking thread: {e}")
        traceback.print_exc()
        backtrack_success = False
    finally:
        backtrack_running = False
        backtrack_finished = True
        print(f"Fill Animation: Backtracking finished. Success: {backtrack_success}")
        if not backtrack_success and not animation_path:
             animation_path.append([EMPTY_SLOT] * 9)

# --- Drawing Functions ---
def draw_grid(screen_param, tiles_param, puzzle_font_param):
    for tile in tiles_param:
        tile.draw(screen_param, puzzle_font_param)

def draw_target_editor(screen_param, editor_tiles_param, editor_state_param, selected_idx_param,
                       title_font_param, font_param, info_font_param, puzzle_font_param, button_font_param,
                       start_btn_param, back_btn_param):
    screen_param.fill(DARK_BG)
    title_surf = title_font_param.render("Chọn Trạng Thái Đích", True, SECONDARY)
    screen_param.blit(title_surf, title_surf.get_rect(centerx=WIDTH // 2, y=70))
    instructions = ["Click ô để chọn, nhập số (1-9) để thay đổi.",
                   "Số nhập sẽ đổi chỗ với số hiện tại.",
                   "Phải là hoán vị hợp lệ của 1-9.",
                   "Nhấn 'Bắt đầu hoạt ảnh' để xem.",]
    line_y = 120
    for text in instructions:
        line_surf = info_font_param.render(text, True, LIGHT_GRAY)
        screen_param.blit(line_surf, line_surf.get_rect(centerx=WIDTH // 2, y=line_y))
        line_y += 30
    if not editor_tiles_param: return
    tile_size = editor_tiles_param[0].size
    puzzle_width = tile_size * 3; puzzle_height = tile_size * 3
    start_x = (WIDTH - puzzle_width) // 2; start_y = line_y + 40
    for i, tile in enumerate(editor_tiles_param):
        row, col = divmod(i, 3)
        tile.rect.topleft = (start_x + col * tile_size, start_y + row * tile_size)
        tile.inner_rect.center = tile.rect.center
        tile.draw(screen_param, puzzle_font_param)
        if i == selected_idx_param:
            highlight_rect = tile.rect.inflate(6, 6)
            pygame.draw.rect(screen_param, PRIMARY, highlight_rect, border_radius=12, width=3)
    is_valid = is_valid_puzzle_state(editor_state_param)
    status_text = "Trạng thái hợp lệ (1-9)" if is_valid else "Trạng thái không hợp lệ (thiếu/trùng số 1-9)"
    status_color = TILE_SOLVED if is_valid else RED
    status_surf = font_param.render(status_text, True, status_color)
    status_rect = status_surf.get_rect(center=(WIDTH // 2, start_y + puzzle_height + 40))
    screen_param.blit(status_surf, status_rect)
    button_y = status_rect.bottom + 30
    button_total_width = start_btn_param.rect.width + back_btn_param.rect.width + 20
    start_btn_param.rect.topleft = (WIDTH // 2 - button_total_width // 2, button_y)
    back_btn_param.rect.topleft = (start_btn_param.rect.right + 20, button_y)
    start_btn_param.check_hover(pygame.mouse.get_pos())
    back_btn_param.check_hover(pygame.mouse.get_pos())
    start_btn_param.draw(screen_param, button_font_param)
    back_btn_param.draw(screen_param, button_font_param)

def draw_filling_animation(screen_param, anim_tiles_param, current_step_param, total_steps_param,
                           target_state_param, auto_mode_param, puzzle_font_param, font_param,
                           info_font_param, button_font_param, auto_btn_param, next_btn_param,
                           reset_btn_param, back_btn_param):
    screen_param.fill(DARK_BG)
    title_surf = title_font.render("Hoạt ảnh điền số Backtracking", True, SECONDARY)
    screen_param.blit(title_surf, title_surf.get_rect(centerx=WIDTH // 2, y=50))
    if anim_tiles_param:
        tile_size = anim_tiles_param[0].size
        puzzle_width = tile_size * 3
        puzzle_height = tile_size * 3
        start_x = (WIDTH - puzzle_width) // 2
        start_y = 150
        for i, tile in enumerate(anim_tiles_param):
            row, col = divmod(i, 3)
            tile.rect.topleft = (start_x + col * tile_size, start_y + row * tile_size)
            tile.inner_rect.center = tile.rect.center
        draw_grid(screen_param, anim_tiles_param, puzzle_font_param)
    info_y = start_y + puzzle_height + 40 if anim_tiles_param else 200
    target_str = ", ".join(map(str, target_state_param))
    info_text_list = [
        f"Trạng thái đích: ({target_str})",
        f"Bước: {current_step_param} / {total_steps_param}",
    ]
    for i, text in enumerate(info_text_list):
        line_surf = info_font_param.render(text, True, LIGHT_GRAY)
        screen_param.blit(line_surf, line_surf.get_rect(centerx=WIDTH // 2, y=info_y + i * 30))
    button_y = info_y + len(info_text_list) * 30 + 30
    button_total_width = auto_btn_param.rect.width + next_btn_param.rect.width + reset_btn_param.rect.width + back_btn_param.rect.width + 3 * 20
    start_buttons_x = (WIDTH - button_total_width) // 2
    auto_btn_param.rect.topleft = (start_buttons_x, button_y)
    next_btn_param.rect.topleft = (auto_btn_param.rect.right + 20, button_y)
    reset_btn_param.rect.topleft = (next_btn_param.rect.right + 20, button_y)
    back_btn_param.rect.topleft = (reset_btn_param.rect.right + 20, button_y)
    auto_btn_param.text = "Auto: On" if auto_mode_param else "Auto: Off"
    for btn in [auto_btn_param, next_btn_param, reset_btn_param, back_btn_param]:
        btn.check_hover(pygame.mouse.get_pos())
        btn.draw(screen_param, button_font_param)

def init_number_tiles(state_param, offset_x, offset_y, tile_size_param):
    tiles_list = []
    for i, val in enumerate(state_param):
        row, col = divmod(i, 3)
        x = offset_x + col * tile_size_param
        y = offset_y + row * tile_size_param
        tile = AnimatedNumberTile(val, x, y, tile_size_param)
        tiles_list.append(tile)
    return tiles_list

def update_animation_tiles(anim_tiles_param, prev_state_param, current_state_param):
    if not anim_tiles_param or len(prev_state_param) != 9 or len(current_state_param) != 9:
        return
    for i in range(9):
        if prev_state_param[i] != current_state_param[i]:
            trigger = (prev_state_param[i] == EMPTY_SLOT and current_state_param[i] != EMPTY_SLOT)
            anim_tiles_param[i].set_value(current_state_param[i], trigger_animation=trigger)
            if prev_state_param[i] != EMPTY_SLOT and current_state_param[i] == EMPTY_SLOT:
                 anim_tiles_param[i].set_value(EMPTY_SLOT, trigger_animation=False)
                 anim_tiles_param[i].highlight = True
        else:
            anim_tiles_param[i].highlight = False

# --- Main Function for fill.py ---
def fill_main():
    global screen, clock, font, title_font, puzzle_font, button_font, info_font
    global backtrack_thread, backtrack_running, backtrack_finished, backtrack_success, animation_path

    current_view = "target_editor"
    target_state = tuple(range(1, 10))
    editable_target_state = list(target_state)
    editor_selected_idx = -1
    editor_tile_size = min(WIDTH * 0.5, HEIGHT * 0.5) / 3
    editor_puzzle_width = editor_tile_size * 3
    editor_start_x = (WIDTH - editor_puzzle_width) // 2
    editor_start_y = 280
    editor_tiles = init_number_tiles(editable_target_state, editor_start_x, editor_start_y, editor_tile_size)
    animation_tiles = []
    anim_tile_size = min(WIDTH * 0.6, HEIGHT * 0.6) / 3
    anim_puzzle_width = anim_tile_size * 3
    anim_start_x = (WIDTH - anim_puzzle_width) // 2
    anim_start_y = 150
    current_animation_step = 0
    auto_mode = True
    last_switch_time = 0
    anim_step_interval_ms = 600

    editor_button_width = 200; editor_button_height = 45
    start_anim_btn = Button(0, 0, editor_button_width, editor_button_height, "Bắt đầu hoạt ảnh")
    back_main_btn_editor = Button(0, 0, 180, editor_button_height, "Về Menu Chính")
    anim_button_width = 120; anim_button_height = 40
    auto_btn = Button(0, 0, anim_button_width, anim_button_height, "Auto: On")
    next_btn = Button(0, 0, anim_button_width, anim_button_height, "Tiếp theo")
    reset_btn = Button(0, 0, anim_button_width, anim_button_height, "Reset")
    back_editor_btn = Button(0, 0, anim_button_width, anim_button_height, "Chọn Lại Đích")
    message_box = MessageBox(450, 200, "Thông báo", "")

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                if backtrack_thread and backtrack_thread.is_alive():
                    backtrack_running = False
                    backtrack_thread.join(timeout=0.5)
            if message_box.active:
                if message_box.handle_event(event): continue
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_click = True
            if current_view == "target_editor":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif editor_selected_idx != -1 and pygame.K_1 <= event.key <= pygame.K_9:
                        new_val = event.key - pygame.K_0
                        current_val = editable_target_state[editor_selected_idx]
                        if new_val != current_val:
                            try:
                                swap_idx = editable_target_state.index(new_val)
                                editable_target_state[editor_selected_idx] = new_val
                                editable_target_state[swap_idx] = current_val
                                editor_tiles[editor_selected_idx].set_value(new_val)
                                editor_tiles[swap_idx].set_value(current_val)
                            except ValueError:
                                message_box.message = f"Số {new_val} không tồn tại để hoán đổi."; message_box.active = True
                        editor_selected_idx = -1
                if mouse_click:
                    if start_anim_btn.is_clicked(mouse_pos, True):
                        if is_valid_puzzle_state(editable_target_state):
                            target_state = tuple(editable_target_state)
                            if backtrack_thread is None or not backtrack_thread.is_alive():
                                print("Fill Animation: Starting backtracking thread...")
                                animation_path.clear()
                                current_animation_step = 0
                                backtrack_finished = False
                                backtrack_thread = threading.Thread(target=run_backtracking_thread, args=(target_state,), daemon=True)
                                backtrack_thread.start()
                                current_view = "filling_animation"
                                animation_tiles = init_number_tiles([EMPTY_SLOT] * 9, anim_start_x, anim_start_y, anim_tile_size)
                                last_switch_time = time.time() * 1000
                            else:
                                print("Fill Animation: Backtracking thread already running.")
                        else:
                            message_box.message = "Trạng thái đích không hợp lệ (1-9)."; message_box.active = True
                    elif back_main_btn_editor.is_clicked(mouse_pos, True):
                        running = False
                    else:
                        editor_selected_idx = -1
                        for i, tile in enumerate(editor_tiles):
                            if tile.rect.collidepoint(mouse_pos):
                                editor_selected_idx = i
                                break
            elif current_view == "filling_animation":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        current_view = "target_editor"
                        if backtrack_thread and backtrack_thread.is_alive():
                            backtrack_running = False
                            backtrack_thread.join(timeout=0.5)
                        backtrack_thread = None
                        backtrack_finished = True
                if mouse_click:
                    if auto_btn.is_clicked(mouse_pos, True):
                        auto_mode = not auto_mode
                        if auto_mode: last_switch_time = time.time() * 1000
                    elif next_btn.is_clicked(mouse_pos, True) and not auto_mode:
                        if backtrack_finished and animation_path and current_animation_step < len(animation_path) - 1:
                            current_animation_step += 1
                            prev_st = animation_path[current_animation_step - 1]
                            curr_st = animation_path[current_animation_step]
                            update_animation_tiles(animation_tiles, prev_st, curr_st)
                    elif reset_btn.is_clicked(mouse_pos, True):
                        current_animation_step = 0
                        last_switch_time = time.time() * 1000
                        for tile in animation_tiles:
                            tile.set_value(EMPTY_SLOT, trigger_animation=False)
                            tile.highlight = False
                        
                        if (backtrack_thread is None or not backtrack_thread.is_alive()):
                             print("Fill Animation: Resetting and restarting backtracking thread...")
                             animation_path.clear()
                             backtrack_finished = False
                             backtrack_thread = threading.Thread(target=run_backtracking_thread, args=(target_state,), daemon=True)
                             backtrack_thread.start()
                        elif animation_path:
                            update_animation_tiles(animation_tiles, [EMPTY_SLOT]*9, animation_path[0])

                    elif back_editor_btn.is_clicked(mouse_pos, True):
                        current_view = "target_editor"
                        if backtrack_thread and backtrack_thread.is_alive():
                            backtrack_running = False
                            backtrack_thread.join(timeout=0.5)
                        backtrack_thread = None
                        backtrack_finished = True

        if current_view == "filling_animation":
            for tile in animation_tiles:
                tile.update()
            now_ms = time.time() * 1000
            if auto_mode and backtrack_finished and animation_path and current_animation_step < len(animation_path) - 1:
                if now_ms - last_switch_time >= anim_step_interval_ms:
                    current_animation_step += 1
                    prev_st = animation_path[current_animation_step - 1]
                    curr_st = animation_path[current_animation_step]
                    update_animation_tiles(animation_tiles, prev_st, curr_st)
                    last_switch_time = now_ms
        screen.fill(DARK_BG)
        if current_view == "target_editor":
            draw_target_editor(screen, editor_tiles, editable_target_state, editor_selected_idx,
                               title_font, font, info_font, puzzle_font, button_font,
                               start_anim_btn, back_main_btn_editor)
        elif current_view == "filling_animation":
            if backtrack_thread and backtrack_thread.is_alive():
                 loading_text = title_font.render("Đang tạo hoạt ảnh...", True, YELLOW)
                 screen.blit(loading_text, loading_text.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
            else:
                 total_steps = max(0, len(animation_path) - 1) if animation_path else 0
                 draw_filling_animation(screen, animation_tiles, current_animation_step, total_steps, target_state, auto_mode,
                                        puzzle_font, font, info_font, button_font,
                                        auto_btn, next_btn, reset_btn, back_editor_btn)
        if message_box.active:
            message_box.draw(screen, title_font, font, button_font)
        pygame.display.flip()
        clock.tick(60)

    if backtrack_thread and backtrack_thread.is_alive():
        backtrack_running = False
        backtrack_thread.join(timeout=0.5)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    pygame.init()
    pygame.font.init()
    try:
        screen_info = pygame.display.Info()
        WIDTH, HEIGHT = screen_info.current_w, screen_info.current_h
        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.SRCALPHA)
    except pygame.error:
        print("Warning: Fullscreen failed. Using 1280x720 windowed.")
        WIDTH, HEIGHT = 1280, 720
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Fill Animation Visualizer")
    clock = pygame.time.Clock()
    try:
        font_name_sys = "Arial";
        if font_name_sys not in pygame.font.get_fonts():
            available_fonts = pygame.font.get_fonts(); common_fonts = ["freesans", "helvetica", "dejavusans", "verdana", "sans"]; font_name_sys = pygame.font.get_default_font();
            for cf in common_fonts:
                 if cf.lower() in [f.lower() for f in available_fonts]: font_name_sys = cf; break
        print(f"Using font: {font_name_sys}")
        font = pygame.font.SysFont(font_name_sys, 22); title_font = pygame.font.SysFont(font_name_sys, 44, bold=True)
        puzzle_font = pygame.font.SysFont(font_name_sys, 60, bold=True)
        button_font = pygame.font.SysFont(font_name_sys, 20); info_font = pygame.font.SysFont(font_name_sys, 22)
    except Exception as e: print(f"Font error: {e}. Using default."); font = pygame.font.Font(None, 24); title_font = pygame.font.Font(None, 44); puzzle_font = pygame.font.Font(None, 60); button_font = pygame.font.Font(None, 20); info_font = pygame.font.Font(None, 22)
    fill_main()