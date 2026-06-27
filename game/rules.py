def is_empty(board, r, c):
    if r in (-1, board.rows) or c in (-1, board.cols):
        return True
    return 0 <= r < board.rows and 0 <= c < board.cols and board.is_empty(r, c)

def get_line(board, r1, c1, r2, c2):
    if r1 == r2:
        step = 1 if c1 <= c2 else -1
        path = [(r1, c) for c in range(c1, c2 + step, step)]
        if all(is_empty(board, r, c) for r, c in path[1:-1]):
            return path
    elif c1 == c2:
        step = 1 if r1 <= r2 else -1
        path = [(r, c1) for r in range(r1, r2 + step, step)]
        if all(is_empty(board, r, c) for r, c in path[1:-1]):
            return path
    return None

def find_path(board, r1, c1, r2, c2):
    if board.get(r1, c1) != board.get(r2, c2) or board.get(r1, c1) == 0:
        return None

    p = get_line(board, r1, c1, r2, c2)
    if p: return p

    for cr, cc in [(r1, c2), (r2, c1)]:
        if is_empty(board, cr, cc):
            p1, p2 = get_line(board, r1, c1, cr, cc), get_line(board, cr, cc, r2, c2)
            if p1 and p2:
                return p1[:-1] + p2

    for c in range(-1, board.cols + 1):
        if all(is_empty(board, r, c) for r in (r1, r2) if (r, c) not in [(r1, c1), (r2, c2)]):
            p1, p2, p3 = get_line(board, r1, c1, r1, c), get_line(board, r1, c, r2, c), get_line(board, r2, c, r2, c2)
            if p1 and p2 and p3:
                return p1[:-1] + p2[:-1] + p3

    for r in range(-1, board.rows + 1):
        if all(is_empty(board, r, c) for c in (c1, c2) if (r, c) not in [(r1, c1), (r2, c2)]):
            p1, p2, p3 = get_line(board, r1, c1, r, c1), get_line(board, r, c1, r, c2), get_line(board, r, c2, r2, c2)
            if p1 and p2 and p3:
                return p1[:-1] + p2[:-1] + p3

    return None

def can_connect(board, r1, c1, r2, c2):
    return find_path(board, r1, c1, r2, c2) is not None


