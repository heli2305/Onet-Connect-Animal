import pygame
from game.board import ANIMAL_NAMES

# ─────────────────────────────────────────────────────────────────
# HẰNG SỐ LAYOUT
# ─────────────────────────────────────────────────────────────────
SCREEN_W = 1200
SCREEN_H = 800
LEFT_W   = 180       # panel trái
RIGHT_W  = 400       # panel phải
CENTER_W = SCREEN_W - LEFT_W - RIGHT_W   # = 620
BOARD_H  = 540       # chiều cao vùng bàn cờ
BOTTOM_H = SCREEN_H - BOARD_H           # = 260

# ─────────────────────────────────────────────────────────────────
# BẢNG MÀU — đặt tên rõ để dễ đọc code
# ─────────────────────────────────────────────────────────────────
BG         = ( 30,  30,  40)   # nền tổng thể
PANEL      = ( 40,  42,  54)   # nền panel
PANEL2     = ( 35,  37,  48)   # nền panel tối hơn (bottom)
BORDER     = ( 70,  72,  90)   # màu viền / đường kẻ

CELL_NORMAL = ( 55,  90, 160)  # ô có thú — xanh dương
CELL_SELECT = (240, 190,  50)  # ô đang chọn — vàng
CELL_PATH   = ( 50, 170, 100)  # ô trên đường nối — xanh lá
CELL_EMPTY  = ( 25,  26,  34)  # ô trống

LINE_PATH   = ( 80, 230, 140)  # màu đường nối (lines)

BLUE        = ( 80, 140, 220)  # nhấn — xanh dương
GREEN       = ( 60, 200, 110)  # thành công
RED         = (210,  65,  65)  # thất bại / dừng
ORANGE      = (220, 150,  50)  # đang chạy

WHITE       = (235, 238, 245)
GRAY        = (150, 155, 170)
DARK_GRAY   = ( 90,  94, 110)

# ─────────────────────────────────────────────────────────────────
# HÀM VẼ TIỆN ÍCH — dùng nội bộ trong file này
# ─────────────────────────────────────────────────────────────────
def _fill(surf, color, x, y, w, h, radius=0):
    """Vẽ hình chữ nhật tô màu."""
    pygame.draw.rect(surf, color, (x, y, w, h), border_radius=radius)

def _outline(surf, color, x, y, w, h, radius=0, width=1):
    """Vẽ viền hình chữ nhật."""
    pygame.draw.rect(surf, color, (x, y, w, h), width=width, border_radius=radius)

def _text(surf, txt, font, color, x, y):
    """Vẽ 1 dòng chữ."""
    img = font.render(str(txt), True, color)
    surf.blit(img, (x, y))
    return img.get_width()   # trả về chiều rộng để căn chỉnh nếu cần


# ─────────────────────────────────────────────────────────────────
# TÍNH VỊ TRÍ Ô TRÊN MÀN HÌNH — hàm PUBLIC (main.py cũng dùng)
# ─────────────────────────────────────────────────────────────────
def cell_rect(board, r, c):
    """
    Trả về pygame.Rect của ô (r, c) trên màn hình.

    Tự động tính kích thước ô sao cho bàn cờ vừa khít
    vào vùng CENTER_TOP và được căn giữa.
    """
    padding  = 12
    area_x   = LEFT_W + padding
    area_y   = 30 + padding                          # 30 = chỗ cho title
    area_w   = CENTER_W - 2 * padding
    area_h   = BOARD_H - 30 - 2 * padding

    # Kích thước 1 ô: tính theo cols+2 và rows+2 để chừa trống 1 ô xung quanh làm đường nối ngoài
    cell_size = min(area_w // (board.cols + 2),
                    area_h // (board.rows + 2),
                    85)                              # tối đa 85px

    # Căn giữa bàn cờ trong vùng
    offset_x = area_x + (area_w - cell_size * board.cols) // 2
    offset_y = area_y + (area_h - cell_size * board.rows) // 2

    return pygame.Rect(
        offset_x + c * cell_size + 2,
        offset_y + r * cell_size + 2,
        cell_size - 4,
        cell_size - 4,
    )


# ─────────────────────────────────────────────────────────────────
# CLASS VISUALIZER
# ─────────────────────────────────────────────────────────────────
class Visualizer:
    """
    Quản lý toàn bộ việc vẽ giao diện.

    Cách dùng:
        viz = Visualizer()              # gọi 1 lần khi khởi động
        viz.draw(screen, ...)           # gọi mỗi frame trong vòng lặp
    """

    def __init__(self):
        # Khởi tạo font — chỉ dùng font hệ thống
        self.font_title = pygame.font.SysFont("segoeui", 16, bold=True)
        self.font_main  = pygame.font.SysFont("segoeui", 15)
        self.font_small = pygame.font.SysFont("segoeui", 11)
        self.font_mono  = pygame.font.SysFont("couriernew", 14)
        self.font_emoji = pygame.font.SysFont("segoeuiemoji", 40)

        # --- NẠP ẢNH PNG TỪ THƯ MỤC ASSETS ---
        import os
        self.animal_images = {}
        self.assets_dir = "game/assets/icons_png"
        self.use_images = os.path.exists(self.assets_dir)

        if self.use_images:
            for name in ANIMAL_NAMES:
                path = os.path.join(self.assets_dir, f"{name}.png")
                if os.path.exists(path):
                    try:
                        # Load ảnh và tối ưu kênh alpha cho ảnh trong suốt
                        img = pygame.image.load(path).convert_alpha()
                        self.animal_images[name] = img
                    except Exception as e:
                        print(f"Lỗi load ảnh {name}.png: {e}")

    # ══════════════════════════════════════════════════════════════
    # HÀM CHÍNH — gọi mỗi frame
    # ══════════════════════════════════════════════════════════════
    def draw(self, screen, state, selected_cell, path_cells, path_animal_id,
             result, log_lines, log_scroll,
             algo_list, selected_algo, is_running,
             is_analysis_mode=False, analysis_step=0, active_log_idx=None):
        """
        Vẽ toàn bộ giao diện lên screen.

        Tham số:
            screen        : pygame.Surface (cửa sổ chính)
            state         : GameState hiện tại
            selected_cell : (r,c) ô đang chọn, hoặc None
            path_cells    : list (r,c) trên đường nối đang hiển thị
            result        : SearchResult sau khi chạy xong, hoặc None
            log_lines     : list[str] các dòng log hiển thị panel phải
            log_scroll    : int số dòng đã cuộn
            algo_list     : list (tên, hàm) thuật toán
            selected_algo : int index thuật toán đang chọn
            is_running    : bool đang chạy thuật toán hay không
        """
        screen.fill(BG)
        self._draw_left(screen, algo_list, selected_algo, is_running, result, is_analysis_mode, analysis_step)
        self._draw_board(screen, state, selected_cell, path_cells, path_animal_id)
        self._draw_bottom(screen, state, result)
        self._draw_right(screen, log_lines, log_scroll, is_analysis_mode, active_log_idx)

    # ══════════════════════════════════════════════════════════════
    # PANEL TRÁI — nút chọn thuật toán + nút điều khiển
    # ══════════════════════════════════════════════════════════════
    def _draw_left(self, screen, algo_list, selected_algo, is_running, result=None, is_analysis_mode=False, analysis_step=0):
        # Nền panel
        _fill(screen, PANEL, 0, 0, LEFT_W, SCREEN_H)
        _outline(screen, BORDER, 0, 0, LEFT_W, SCREEN_H)

        # Tiêu đề
        _text(screen, "THUẬT TOÁN", self.font_title, GRAY, 8, 8)
        pygame.draw.line(screen, BORDER, (4, 26), (LEFT_W - 4, 26))

        # Danh sách thuật toán
        y = 32
        for i, (name, _) in enumerate(algo_list):
            item = pygame.Rect(5, y, LEFT_W - 10, 30)
            if i == selected_algo:
                # Ô được chọn: tô nền xanh
                _fill(screen, BLUE, item.x, item.y, item.w, item.h, radius=5)
                _text(screen, name, self.font_main, WHITE, 10, y + 6)
            else:
                _text(screen, name, self.font_main, GRAY, 10, y + 6)
            y += 33

        # ── KHU VỰC PHÂN TÍCH THUẬT TOÁN ──
        total_steps = len(result.search_steps) if (result and hasattr(result, "search_steps")) else 0
        
        # Nút chuyển chế độ
        btn_mode_y = 460
        btn_mode_color = BLUE if (is_analysis_mode and total_steps > 0) else DARK_GRAY
        _fill(screen, btn_mode_color, 5, btn_mode_y, LEFT_W - 10, 30, radius=6)
        _outline(screen, BORDER, 5, btn_mode_y, LEFT_W - 10, 30, radius=6)
        
        mode_label = "Chế độ: Phân tích" if (is_analysis_mode and total_steps > 0) else "Chế độ: Xem giải"
        _text(screen, mode_label, self.font_small, WHITE, 14, btn_mode_y + 7)

        # Hiển thị số bước & nút tiến lùi
        if total_steps > 0:
            # Nhãn số bước
            _text(screen, f"Bước: {analysis_step + 1} / {total_steps}", self.font_main, WHITE, 10, 505)
            
            # Nút Trước / Sau
            btn_w = (LEFT_W - 10) // 2 - 2
            _fill(screen, DARK_GRAY, 5, 535, btn_w, 28, radius=6)
            _text(screen, "<- Trước", self.font_small, WHITE, 10, 541)
            
            _fill(screen, DARK_GRAY, 5 + btn_w + 4, 535, btn_w, 28, radius=6)
            _text(screen, "Sau ->", self.font_small, WHITE, 5 + btn_w + 14, 541)
            
            # Hướng dẫn
            _text(screen, "Mũi tên <-/-> để duyệt", self.font_small, GRAY, 10, 575)
        else:
            _text(screen, "Chạy AI để phân tích", self.font_small, GRAY, 10, 505)

        # ── Nút Chạy AI ──
        btn_color = ORANGE if is_running else GREEN
        _fill(screen, btn_color, 5, SCREEN_H - 118, LEFT_W - 10, 34, radius=6)
        label = "Đang chạy..." if is_running else "Chạy AI"
        _text(screen, label, self.font_main, WHITE, 14, SCREEN_H - 110)

        # ── Nút Bàn mới ──
        _fill(screen, DARK_GRAY, 5, SCREEN_H - 78, LEFT_W - 10, 30, radius=6)
        _text(screen, "Bàn mới  [N]", self.font_main, WHITE, 10, SCREEN_H - 71)

        # ── Nút Dừng ──
        _fill(screen, RED, 5, SCREEN_H - 42, LEFT_W - 10, 30, radius=6)
        _text(screen, "Dừng  [S]", self.font_main, WHITE, 14, SCREEN_H - 35)

    # ══════════════════════════════════════════════════════════════
    # PANEL GIỮA TRÊN — bàn cờ + animation đường nối
    # ══════════════════════════════════════════════════════════════
    def _draw_board(self, screen, state, selected_cell, path_cells, path_animal_id=0):
        board    = state.board
        path_set = set(tuple(p) for p in path_cells)

        # Tiêu đề vùng
        _text(screen, "MÀN HÌNH MINH HOẠ",
              self.font_title, GRAY, LEFT_W + 8, 8)

        # ── Vẽ từng ô ──
        for r in range(board.rows):
            for c in range(board.cols):
                cr  = cell_rect(board, r, c)
                val = board.get(r, c)

                # Chọn màu nền ô
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

                # Vẽ icon con thú (PNG)
                draw_val = val
                if val == 0 and is_endpoint:
                    draw_val = path_animal_id

                if draw_val != 0:
                    animal = ANIMAL_NAMES[(draw_val - 1) % len(ANIMAL_NAMES)]
                    if self.use_images and animal in self.animal_images:
                        img = self.animal_images[animal]
                        orig_w, orig_h = img.get_size()
                        # Tính tỷ lệ scale giữ nguyên aspect ratio (tối đa cr.w - 8)
                        target_max = cr.w - 8
                        scale = min(target_max / orig_w, target_max / orig_h)
                        new_w = int(orig_w * scale)
                        new_h = int(orig_h * scale)
                        
                        img_scaled = pygame.transform.smoothscale(img, (new_w, new_h))
                        screen.blit(img_scaled, (
                            cr.centerx - img_scaled.get_width() // 2,
                            cr.centery - img_scaled.get_height() // 2,
                        ))                  

        # ── Vẽ đường nối ──
        if len(path_cells) >= 2:
            points = []
            for (r, c) in path_cells:
                cr = cell_rect(board, r, c)
                points.append(cr.center)
            pygame.draw.lines(screen, LINE_PATH, False, points, 3)

        # ── Viền vùng bàn cờ ──
        _outline(screen, BORDER, LEFT_W, 0, CENTER_W, BOARD_H)

    # ══════════════════════════════════════════════════════════════
    # PANEL GIỮA DƯỚI — kết quả chạy thuật toán
    # ══════════════════════════════════════════════════════════════
    def _draw_bottom(self, screen, state, result):
        _fill(screen, PANEL2, LEFT_W, BOARD_H, CENTER_W, BOTTOM_H)
        _outline(screen, BORDER, LEFT_W, BOARD_H, CENTER_W, BOTTOM_H)
        pygame.draw.line(screen, BORDER,
                         (LEFT_W, BOARD_H), (LEFT_W + CENTER_W, BOARD_H))

        _text(screen, "KẾT QUẢ CHẠY",
              self.font_title, GRAY, LEFT_W + 8, BOARD_H + 8)
        pygame.draw.line(screen, BORDER,
                         (LEFT_W + 4, BOARD_H + 26),
                         (LEFT_W + CENTER_W - 4, BOARD_H + 26))

        if result:
            # Hiển thị 6 chỉ số thống kê xếp 3 cột × 2 hàng
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
                x  = LEFT_W + 10 + col * col_w
                yy = BOARD_H + 40 + row * 65

                _text(screen, label, self.font_small, GRAY, x, yy)

                # Màu giá trị: xanh = tốt, đỏ = xấu, trắng = bình thường
                if "Thành" in value:
                    val_color = GREEN
                elif "Thất" in value:
                    val_color = RED
                else:
                    val_color = WHITE

                _text(screen, value, self.font_title, val_color, x, yy + 18)

        else:
            # Chưa chạy → hiển thị thông tin bàn cờ hiện tại
            board      = state.board
            pairs_left = board.num_remaining_tiles() // 2
            _text(screen,
                  f"Bàn {board.rows}×{board.cols}  |  "
                  f"Cặp còn lại: {pairs_left}  |  "
                  f"Chọn thuật toán và nhấn Chạy AI",
                  self.font_main, GRAY, LEFT_W + 10, BOARD_H + 34)

    # ══════════════════════════════════════════════════════════════
    # PANEL PHẢI — log quá trình các bước chạy
    # ══════════════════════════════════════════════════════════════
    def _draw_right(self, screen, log_lines, log_scroll, is_analysis_mode=False, active_log_idx=None):
        rx = SCREEN_W - RIGHT_W   # tọa độ x bắt đầu panel phải

        _fill(screen, PANEL, rx, 0, RIGHT_W, SCREEN_H)
        _outline(screen, BORDER, rx, 0, RIGHT_W, SCREEN_H)

        _text(screen, "QUÁ TRÌNH CHẠY",
              self.font_title, GRAY, rx + 8, 8)
        pygame.draw.line(screen, BORDER, (rx + 4, 26), (SCREEN_W - 4, 26))

        # ── Vùng hiển thị log (có clip để không tràn ra ngoài) ──
        log_area = pygame.Rect(rx + 4, 30, RIGHT_W - 8, SCREEN_H - 48)
        old_clip = screen.get_clip()
        screen.set_clip(log_area)

        y = 32
        line_h = 15   # chiều cao 1 dòng log

        for i, line in enumerate(log_lines):
            if i < log_scroll:
                continue    # bỏ qua các dòng đã cuộn qua

            # Cắt bớt nếu dòng quá dài để không tràn sang màn hình
            if len(line) > 65:
                line = line[:63] + "…"

            # Vẽ nền highlight nếu là dòng log đang phân tích active
            is_active = (is_analysis_mode and active_log_idx is not None and i == active_log_idx)

            # Màu log theo nội dung — giúp phân biệt nhanh khi nhìn
            if is_active:
                _fill(screen, (60, 75, 100), rx + 6, y - 1, RIGHT_W - 12, line_h, radius=4)
                color = CELL_SELECT # màu vàng nổi bật
            elif any(k in line for k in ("Bắt đầu", "Chọn")):
                color = BLUE
            elif any(k in line for k in ("Xong", "Nối", "goal")):
                color = GREEN
            elif any(k in line for k in ("Lỗi", "Không", "Thất")):
                color = RED
            elif "Mở rộng" in line:
                color = (160, 210, 160)   # xanh nhạt — log chi tiết thuật toán
            elif "Quay lại" in line or "backtrack" in line.lower():
                color = (220, 160, 80)    # cam — backtrack
            else:
                color = GRAY

            _text(screen, line, self.font_small, color, rx + 8, y)
            y += line_h

            if y > SCREEN_H - 24:
                break   # hết chỗ hiển thị

        screen.set_clip(old_clip)

        # Dòng hướng dẫn cuộn ở dưới cùng panel
        footer_text = f"↑↓ cuộn  |  {len(log_lines)} dòng"
        if is_analysis_mode and active_log_idx is not None:
            footer_text += f"  |  Đang xem: {active_log_idx + 1}"
        _text(screen, footer_text,
              self.font_small, DARK_GRAY, rx + 8, SCREEN_H - 16)
