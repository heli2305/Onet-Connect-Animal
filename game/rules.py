from collections import deque

def find_path(board, r1, c1, r2, c2):
    """
    Tìm đường nối hợp lệ từ (r1,c1) đến (r2,c2).
    Điều kiện:
      - Hai ô phải cùng loại thú
      - Đường đi không quá 2 lần rẽ
      - Không đi qua ô có thú (trừ điểm đích)
    Trả về: list các tọa độ [(r,c),...] nếu tìm được, None nếu không.
    """
    if board.get(r1, c1) != board.get(r2, c2):
        return None
    if board.get(r1, c1) == 0:
        return None

    rows, cols = board.rows, board.cols
    DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    # State: (r, c, direction_index, num_turns, path)
    # direction_index = -1 nghĩa là chưa có hướng nào
    queue = deque()
    queue.append((r1, c1, -1, 0, [(r1, c1)]))

    # visited: (r, c, dir, turns) để tránh lặp
    visited = set()

    while queue:
        r, c, cur_dir, turns, path = queue.popleft()

        state = (r, c, cur_dir, turns)
        if state in visited:
            continue
        visited.add(state)

        # Đến đích rồi
        if r == r2 and c == c2:
            return path

        # Đã quá 2 rẽ → bỏ qua
        if turns > 2:
            continue

        for i, (dr, dc) in enumerate(DIRS):
            nr, nc = r + dr, c + dc

            # Kiểm tra biên (cho phép đi ra ngoài rìa tối đa 1 ô)
            if not (-1 <= nr <= rows and -1 <= nc <= cols):
                continue

            # Tính số rẽ mới
            new_turns = turns
            if cur_dir != -1 and cur_dir != i:
                new_turns += 1

            if new_turns > 2:
                continue

            # Ô đích: luôn được đi đến
            if nr == r2 and nc == c2:
                queue.append((nr, nc, i, new_turns, path + [(nr, nc)]))
                continue

            # Ô trống (hoặc ô ngoài rìa): mới được đi qua
            is_outside = (nr == -1 or nr == rows or nc == -1 or nc == cols)
            if is_outside or board.is_empty(nr, nc):
                queue.append((nr, nc, i, new_turns, path + [(nr, nc)]))

    return None  # Không tìm được đường


def can_connect(board, r1, c1, r2, c2):
    """Kiểm tra nhanh có thể nối được không (không cần trả về path)."""
    return find_path(board, r1, c1, r2, c2) is not None
