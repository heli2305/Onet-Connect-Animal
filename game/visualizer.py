import pygame
from game.board import ANIMAL_NAMES

SCREEN_W = 1400
SCREEN_H = 900
LEFT_W   = 270
RIGHT_W  = 430
CENTER_W = SCREEN_W - LEFT_W - RIGHT_W
BOARD_H  = 600
BOTTOM_H = SCREEN_H - BOARD_H
LOG_LINE_H = 21

BG         = ( 30,  30,  40)
PANEL      = ( 40,  42,  54)
PANEL2     = ( 35,  37,  48)
BORDER     = ( 70,  72,  90) 

CELL_NORMAL = ( 55,  90, 160)  
CELL_SELECT = (240, 190,  50) 
CELL_PATH   = ( 50, 170, 100)  
CELL_EMPTY  = ( 25,  26,  34)  

LINE_PATH   = ( 80, 230, 140)

BLUE        = ( 80, 140, 220) 
GREEN       = ( 60, 200, 110) 
RED         = (210,  65,  65) 
ORANGE      = (220, 150,  50) 

WHITE       = (235, 238, 245)
GRAY        = (150, 155, 170)
DARK_GRAY   = ( 90,  94, 110)


def _fill(surf, color, x, y, w, h, radius=0):
    pygame.draw.rect(surf, color, (x, y, w, h), border_radius=radius)

def _outline(surf, color, x, y, w, h, radius=0, width=1):
    pygame.draw.rect(surf, color, (x, y, w, h), width=width, border_radius=radius)

def _text(surf, txt, font, color, x, y, max_w=None):
    txt_str = str(txt)
    if max_w is not None and font.size(txt_str)[0] > max_w:
        for i in range(len(txt_str), 0, -1):
            sub_txt = txt_str[:i] + "..."
            if font.size(sub_txt)[0] <= max_w:
                txt_str = sub_txt
                break
    img = font.render(txt_str, True, color)
    surf.blit(img, (x, y))
    return img.get_width()   


def cell_rect(board, r, c):
    padding  = 12
    area_x   = LEFT_W + padding
    area_y   = 45 + padding
    area_w   = CENTER_W - 2 * padding
    area_h   = BOARD_H - 45 - 2 * padding

    cell_size = min(area_w // (board.cols + 2),
                    area_h // (board.rows + 2),
                    85)                              

    offset_x = area_x + (area_w - cell_size * board.cols) // 2
    offset_y = area_y + (area_h - cell_size * board.rows) // 2

    return pygame.Rect(
        offset_x + c * cell_size + 2,
        offset_y + r * cell_size + 2,
        cell_size - 4,
        cell_size - 4,
    )



class Visualizer:

    def __init__(self):
        self.font_title = pygame.font.SysFont("segoeui", 18, bold=True)
        self.font_main  = pygame.font.SysFont("segoeui", 16)
        self.font_small = pygame.font.SysFont("segoeui", 12)
        self.font_log   = pygame.font.SysFont("segoeui", 16)
        self.font_mono  = pygame.font.SysFont("couriernew", 14)
        self.font_emoji = pygame.font.SysFont("segoeuiemoji", 40)
        
        self.font_stats_label = pygame.font.SysFont("segoeui", 14)
        self.font_stats_val   = pygame.font.SysFont("segoeui", 20, bold=True)
        self.font_stats_desc  = pygame.font.SysFont("segoeui", 18)
        self.font_stats_header = pygame.font.SysFont("segoeui", 14)
        self.font_btn         = pygame.font.SysFont("segoeui", 16, bold=True)
        self.font_btn_small   = pygame.font.SysFont("segoeui", 13, bold=True)

        import os
        self.animal_images = {}
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.assets_dir = os.path.join(current_dir, "assets", "icons_png")
        self.use_images = os.path.exists(self.assets_dir)

        if self.use_images:
            for name in ANIMAL_NAMES:
                path = os.path.join(self.assets_dir, f"{name}.png")
                if os.path.exists(path):
                    try:
                        img = pygame.image.load(path).convert_alpha()
                        self.animal_images[name] = img
                    except Exception as e:
                        print(f"Lỗi load ảnh {name}.png: {e}")

    def draw(self, screen, state, selected_cell, path_cells, path_animal_id,
             result, log_lines, log_scroll,
             algo_groups, selected_group_idx, selected_algo_idx, opened_group, is_running,
             is_analysis_mode=False, analysis_step=0, active_log_idx=None,
             active_bottom_tab=0, run_history=None, comparison_scroll=0):

        screen.fill(BG)
        self._draw_left(screen, algo_groups, selected_group_idx, selected_algo_idx, opened_group, is_running, result, is_analysis_mode, analysis_step)
        self._draw_board(screen, state, selected_cell, path_cells, path_animal_id)
        self._draw_bottom(screen, state, result, active_bottom_tab, run_history, comparison_scroll)
        self._draw_right(screen, log_lines, log_scroll, is_analysis_mode, active_log_idx)


    def _draw_left(self, screen, algo_groups, selected_group_idx, selected_algo_idx, opened_group, is_running, result=None, is_analysis_mode=False, analysis_step=0):
        _fill(screen, PANEL, 0, 0, LEFT_W, SCREEN_H)
        _outline(screen, BORDER, 0, 0, LEFT_W, SCREEN_H)

        _text(screen, "NHÓM THUẬT TOÁN", self.font_title, GRAY, 12, 12)
        pygame.draw.line(screen, BORDER, (4, 38), (LEFT_W - 4, 38))

        y = 48
        for g_idx, group in enumerate(algo_groups):
            header_rect = pygame.Rect(5, y, LEFT_W - 10, 36)
            is_opened = (opened_group == g_idx)
            
            header_bg = (55, 58, 75) if is_opened else (45, 47, 60)
            _fill(screen, header_bg, header_rect.x, header_rect.y, header_rect.w, header_rect.h, radius=5)
            _outline(screen, BORDER, header_rect.x, header_rect.y, header_rect.w, header_rect.h, radius=5)
            
            arrow = "v" if is_opened else ">"
            _text(screen, arrow, self.font_main, GRAY, 14, y + 7)
            _text(screen, group["name"], self.font_stats_header, WHITE, 30, y + 9, max_w=LEFT_W - 55)
            
            y += 40
            
            if is_opened:
                if not group["algos"]:
                    _text(screen, "(Trống)", self.font_small, DARK_GRAY, 45, y + 4)
                    y += 24
                else:
                    for a_idx, algo in enumerate(group["algos"]):
                        item_rect = pygame.Rect(20, y, LEFT_W - 25, 30)
                        is_selected = (selected_group_idx == g_idx and selected_algo_idx == a_idx)
                        
                        if is_selected:
                            _fill(screen, BLUE, item_rect.x, item_rect.y, item_rect.w, item_rect.h, radius=5)
                            _text(screen, algo["name"], self.font_main, WHITE, 45, y + 4)
                        else:
                            _fill(screen, PANEL, item_rect.x, item_rect.y, item_rect.w, item_rect.h, radius=5)
                            _outline(screen, BORDER, item_rect.x, item_rect.y, item_rect.w, item_rect.h, radius=5)
                            _text(screen, algo["name"], self.font_main, GRAY, 45, y + 4)
                        
                        y += 34

        total_steps = len(result.search_steps) if (result and hasattr(result, "search_steps")) else 0
        
        btn_mode_y = 520
        btn_mode_color = BLUE if (is_analysis_mode and total_steps > 0) else DARK_GRAY
        _fill(screen, btn_mode_color, 5, btn_mode_y, LEFT_W - 10, 34, radius=6)
        _outline(screen, BORDER, 5, btn_mode_y, LEFT_W - 10, 34, radius=6)
        
        mode_label = "Chế độ: Phân tích" if (is_analysis_mode and total_steps > 0) else "Chế độ: Xem giải"
        _text(screen, mode_label, self.font_btn_small, WHITE, 14, btn_mode_y + 9)

        if total_steps > 0:
            _text(screen, f"Bước: {analysis_step + 1} / {total_steps}", self.font_main, WHITE, 10, 570)
            
            btn_w = (LEFT_W - 10) // 2 - 2
            _fill(screen, DARK_GRAY, 5, 600, btn_w, 32, radius=6)
            _text(screen, "<- Trước", self.font_btn_small, WHITE, 10, 608)
            
            _fill(screen, DARK_GRAY, 5 + btn_w + 4, 600, btn_w, 32, radius=6)
            _text(screen, "Sau ->", self.font_btn_small, WHITE, 5 + btn_w + 14, 608)
        else:
            _text(screen, "Chạy AI để phân tích", self.font_small, GRAY, 10, 570)

        btn_color = ORANGE if is_running else GREEN
        _fill(screen, btn_color, 5, SCREEN_H - 158, LEFT_W - 10, 38, radius=6)
        label = "Đang chạy..." if is_running else "Chạy AI"
        _text(screen, label, self.font_btn, WHITE, 14, SCREEN_H - 149)

        _fill(screen, DARK_GRAY, 5, SCREEN_H - 108, LEFT_W - 10, 38, radius=6)
        _text(screen, "Bàn mới  [N]", self.font_btn, WHITE, 10, SCREEN_H - 99)

        _fill(screen, RED, 5, SCREEN_H - 58, LEFT_W - 10, 38, radius=6)
        _text(screen, "Dừng  [S]", self.font_btn, WHITE, 14, SCREEN_H - 49)


    def _draw_board(self, screen, state, selected_cell, path_cells, path_animal_id=0):
        board    = state.board
        path_set = set(tuple(p) for p in path_cells)

        _text(screen, "MÀN HÌNH MINH HOẠ",
              self.font_title, GRAY, LEFT_W + 12, 12)

        for r in range(board.rows):
            for c in range(board.cols):
                cr  = cell_rect(board, r, c)
                val = board.get(r, c)

                is_endpoint = (len(path_cells) >= 2) and ((r, c) == path_cells[0] or (r, c) == path_cells[-1])

                if val == 0 and not is_endpoint:
                    color = CELL_EMPTY
                elif (r, c) in path_set:
                    color = CELL_PATH
                elif selected_cell == (r, c):
                    color = CELL_SELECT
                else:
                    color = CELL_NORMAL

                _fill(screen, color, cr.x, cr.y, cr.w, cr.h, radius=6)
                _outline(screen, BORDER, cr.x, cr.y, cr.w, cr.h, radius=6)

                draw_val = val
                if val == 0 and is_endpoint:
                    draw_val = path_animal_id

                if draw_val != 0:
                    animal = ANIMAL_NAMES[(draw_val - 1) % len(ANIMAL_NAMES)]
                    if self.use_images and animal in self.animal_images:
                        img = self.animal_images[animal]
                        orig_w, orig_h = img.get_size()
                        target_max = cr.w - 8
                        scale = min(target_max / orig_w, target_max / orig_h)
                        new_w = int(orig_w * scale)
                        new_h = int(orig_h * scale)
                        
                        img_scaled = pygame.transform.smoothscale(img, (new_w, new_h))
                        screen.blit(img_scaled, (
                            cr.centerx - img_scaled.get_width() // 2,
                            cr.centery - img_scaled.get_height() // 2,
                        ))                  

        if len(path_cells) >= 2:
            points = []
            for (r, c) in path_cells:
                cr = cell_rect(board, r, c)
                points.append(cr.center)
            pygame.draw.lines(screen, LINE_PATH, False, points, 3)

        _outline(screen, BORDER, LEFT_W, 0, CENTER_W, BOARD_H)


    def _draw_bottom(self, screen, state, result, active_bottom_tab=0, run_history=None, comparison_scroll=0):
        run_history = run_history or []
        _fill(screen, PANEL2, LEFT_W, BOARD_H, CENTER_W, BOTTOM_H)
        _outline(screen, BORDER, LEFT_W, BOARD_H, CENTER_W, BOTTOM_H)
        pygame.draw.line(screen, BORDER,
                         (LEFT_W, BOARD_H), (LEFT_W + CENTER_W, BOARD_H))

        tab1_rect = pygame.Rect(LEFT_W + 12, BOARD_H + 10, 150, 28)
        tab2_rect = pygame.Rect(LEFT_W + 12 + 160, BOARD_H + 10, 150, 28)

        tab1_color = PANEL if active_bottom_tab == 0 else PANEL2
        tab2_color = PANEL if active_bottom_tab == 1 else PANEL2

        _fill(screen, tab1_color, tab1_rect.x, tab1_rect.y, tab1_rect.w, tab1_rect.h, radius=4)
        _outline(screen, BORDER, tab1_rect.x, tab1_rect.y, tab1_rect.w, tab1_rect.h, radius=4)
        _text(screen, "Chi tiết", self.font_btn_small, WHITE, tab1_rect.x + 45, tab1_rect.y + 5)

        _fill(screen, tab2_color, tab2_rect.x, tab2_rect.y, tab2_rect.w, tab2_rect.h, radius=4)
        _outline(screen, BORDER, tab2_rect.x, tab2_rect.y, tab2_rect.w, tab2_rect.h, radius=4)
        _text(screen, "So sánh", self.font_btn_small, WHITE, tab2_rect.x + 45, tab2_rect.y + 5)

        pygame.draw.line(screen, BORDER,
                         (LEFT_W + 4, BOARD_H + 42),
                         (LEFT_W + CENTER_W - 4, BOARD_H + 42))

        if active_bottom_tab == 0:
            if result:
                stats = [
                    ("Thuật toán",    result.algorithm_name),
                    ("Kết quả",       "Thành công" if result.success else "Thất bại"),
                    ("Số bước",       str(result.cost)),
                    ("Nodes mở rộng", str(result.expanded_nodes)),
                    ("Nodes sinh ra", str(result.generated_nodes)),
                    ("Thời gian",     f"{result.time_seconds * 1000:.1f} ms"),
                ]
                col_w = CENTER_W // 3
                for i, (label, value) in enumerate(stats):
                    col = i % 3
                    row = i // 3
                    x  = LEFT_W + 12 + col * col_w
                    yy = BOARD_H + 54 + row * 80

                    _text(screen, label, self.font_stats_label, GRAY, x, yy)

                    if "Thành" in value:
                        val_color = GREEN
                    elif "Thất" in value:
                        val_color = RED
                    else:
                        val_color = WHITE

                    _text(screen, value, self.font_stats_val, val_color, x, yy + 18)

            else:
                board      = state.board
                pairs_left = board.num_remaining_tiles() // 2
                _text(screen,
                      f"Bàn {board.rows}×{board.cols}  |  "
                      f"Cặp còn lại: {pairs_left}  |  "
                      f"Chọn thuật toán và nhấn Chạy AI",
                      self.font_stats_desc, GRAY, LEFT_W + 12, BOARD_H + 54)
        else:
            if len(run_history) > 6:
                ind = f"Cuộn để xem (+{len(run_history) - 6})"
                _text(screen, ind, self.font_small, GRAY, LEFT_W + CENTER_W - 140, BOARD_H + 16)

            x = LEFT_W + 12
            header_y = BOARD_H + 52
            _text(screen, "Thuật toán", self.font_stats_header, GRAY, x, header_y)
            _text(screen, "Trạng thái", self.font_stats_header, GRAY, x + 160, header_y)
            _text(screen, "Số bước", self.font_stats_header, GRAY, x + 270, header_y)
            _text(screen, "Nodes mở", self.font_stats_header, GRAY, x + 360, header_y)
            _text(screen, "Nodes sinh", self.font_stats_header, GRAY, x + 470, header_y)
            _text(screen, "Thời gian", self.font_stats_header, GRAY, x + 580, header_y)

            pygame.draw.line(screen, BORDER,
                             (LEFT_W + 4, BOARD_H + 74),
                             (LEFT_W + CENTER_W - 4, BOARD_H + 74))

            if not run_history:
                _text(screen, "Chưa có dữ liệu so sánh. Hãy chọn thuật toán và nhấn Chạy AI.",
                      self.font_stats_desc, GRAY, LEFT_W + 12, BOARD_H + 85)
            else:
                max_sc = max(0, len(run_history) - 6)
                comparison_scroll = min(comparison_scroll, max_sc)
                start_y = BOARD_H + 80
                row_h = 32
                for idx in range(comparison_scroll, min(len(run_history), comparison_scroll + 6)):
                    r = run_history[idx]
                    y = start_y + (idx - comparison_scroll) * row_h
                    if idx % 2 == 1:
                        _fill(screen, PANEL, LEFT_W + 6, y, CENTER_W - 12, row_h, radius=4)

                    _text(screen, r.algorithm_name, self.font_main, WHITE, x, y + 5, max_w=150)
                    status_txt = "Thành công" if r.success else "Thất bại"
                    status_color = GREEN if r.success else RED
                    _text(screen, status_txt, self.font_main, status_color, x + 160, y + 5)
                    _text(screen, str(r.cost), self.font_main, WHITE, x + 270, y + 5)
                    _text(screen, str(r.expanded_nodes), self.font_main, WHITE, x + 360, y + 5)
                    _text(screen, str(r.generated_nodes), self.font_main, WHITE, x + 470, y + 5)
                    _text(screen, f"{r.time_seconds * 1000:.1f} ms", self.font_main, WHITE, x + 580, y + 5)


    def _draw_right(self, screen, log_lines, log_scroll, is_analysis_mode=False, active_log_idx=None):
        rx = SCREEN_W - RIGHT_W   

        _fill(screen, PANEL, rx, 0, RIGHT_W, SCREEN_H)
        _outline(screen, BORDER, rx, 0, RIGHT_W, SCREEN_H)

        _text(screen, "QUÁ TRÌNH CHẠY",
              self.font_title, GRAY, rx + 12, 12)
        pygame.draw.line(screen, BORDER, (rx + 4, 38), (SCREEN_W - 4, 38))

        log_area = pygame.Rect(rx + 4, 44, RIGHT_W - 8, SCREEN_H - 68)
        old_clip = screen.get_clip()
        screen.set_clip(log_area)

        y = 48
        line_h = LOG_LINE_H

        for i, line in enumerate(log_lines):
            if i < log_scroll:
                continue    

            if len(line) > 65:
                line = line[:63] + "…"

            is_active = (is_analysis_mode and active_log_idx is not None and i == active_log_idx)

            if is_active:
                _fill(screen, (60, 75, 100), rx + 6, y - 1, RIGHT_W - 12, line_h, radius=4)
                color = CELL_SELECT 
            elif any(k in line for k in ("Bắt đầu", "[BFS]", "[A*]", "[CSP]", "[Gán]")):
                color = BLUE
            elif any(k in line for k in ("Xong", "Nối", "goal")):
                color = GREEN
            elif any(k in line for k in ("Lỗi", "Không", "Thất")):
                color = RED
            elif "[Mở rộng]" in line or "[Pop]" in line:
                color = (160, 210, 160)
            elif "[Quay lui]" in line or "backtrack" in line.lower():
                color = (220, 160, 80)
            else:
                color = GRAY

            _text(screen, line, self.font_log, color, rx + 8, y)
            y += line_h

            if y > SCREEN_H - 24:
                break   

        screen.set_clip(old_clip)

        footer_text = f"↑↓ cuộn  |  {len(log_lines)} dòng"
        if is_analysis_mode and active_log_idx is not None:
            footer_text += f"  |  Đang xem: {active_log_idx + 1}"
        _text(screen, footer_text,
              self.font_small, DARK_GRAY, rx + 8, SCREEN_H - 16)
