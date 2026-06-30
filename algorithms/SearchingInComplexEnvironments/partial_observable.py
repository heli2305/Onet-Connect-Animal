from algorithms.base import SearchLogger
from game.state import GameState
from game.rules import can_connect


def partial_observable_search(initial_state: GameState):
    logger = SearchLogger("Partial Observable")
    
    true_board = initial_state.board.clone()
    visible_board = initial_state.board.clone()
    
    # Xác định các ô ẩn (các ô không nằm trên viền)
    hidden_cells = set()
    for r in range(visible_board.rows):
        for c in range(visible_board.cols):
            if 0 < r < visible_board.rows - 1 and 0 < c < visible_board.cols - 1:
                hidden_cells.add((r, c))
                visible_board.board[r][c] = -1  # Gán -1 để đại diện cho ô ẩn
                
    logger.log(
        f"[Partial] Khởi tạo | Ô ẩn: {len(hidden_cells)} | Cặp còn: {true_board.num_remaining_tiles() // 2}",
        state=GameState(visible_board.clone())
    )
    
    actions_taken = []
    
    def get_visible_pairs():
        positions = {}
        for r in range(visible_board.rows):
            for c in range(visible_board.cols):
                v = visible_board.get(r, c)
                if v > 0:
                    positions.setdefault(v, []).append((r, c))
        pairs = []
        for v, pos_list in positions.items():
            for i in range(len(pos_list)):
                for j in range(i + 1, len(pos_list)):
                    pairs.append((*pos_list[i], *pos_list[j]))
        return pairs

    while not true_board.is_solved():
        logger.on_expand()
        
        # Tìm các cặp nối khả thi trên phần bảng nhìn thấy được
        pairs = get_visible_pairs()
        matching_pairs = []
        for (r1, c1, r2, c2) in pairs:
            if can_connect(visible_board, r1, c1, r2, c2):
                matching_pairs.append((r1, c1, r2, c2))
                
        if matching_pairs:
            # Chọn cặp nối đầu tiên
            action = matching_pairs[0]
            r1, c1, r2, c2 = action
            
            # Thực hiện loại bỏ trên cả bảng thật và bảng nhìn thấy
            visible_board.remove(r1, c1, r2, c2)
            true_board.remove(r1, c1, r2, c2)
            actions_taken.append(action)
            
            # Tiết lộ các ô ẩn nằm lân cận ô vừa xóa
            revealed = []
            for r, c in [(r1, c1), (r2, c2)]:
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = r + dr, c + dc
                    if (nr, nc) in hidden_cells:
                        hidden_cells.remove((nr, nc))
                        val = true_board.get(nr, nc)
                        visible_board.board[nr][nc] = val
                        revealed.append(f"({nr},{nc})")
                        
            rev_msg = f" | Lật mở: {', '.join(revealed)}" if revealed else ""
            logger.log(
                f"[Nối] ({r1},{c1})↔({r2},{c2}){rev_msg}",
                state=GameState(visible_board.clone())
            )
            logger.on_generate()
        elif hidden_cells:
            # Nếu bị kẹt nhưng vẫn còn ô ẩn, thực hiện hành động "thăm dò" (Sensing) để lật mở 1 ô ẩn
            # Ưu tiên lật ô ẩn nằm kề cạnh ô trống
            target = None
            for r, c in hidden_cells:
                # Kiểm tra xem có ô lân cận trống nào không
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < visible_board.rows and 0 <= nc < visible_board.cols:
                        if visible_board.get(nr, nc) == 0:
                            target = (r, c)
                            break
                if target:
                    break
            
            if not target:
                target = list(hidden_cells)[0]
                
            hidden_cells.remove(target)
            tr, tc = target
            val = true_board.get(tr, tc)
            visible_board.board[tr][tc] = val
            
            logger.log(
                f"[Sensing] Bị kẹt -> Thăm dò ô ({tr},{tc}) chứa thú",
                state=GameState(visible_board.clone())
            )
            logger.on_generate()
        else:
            # Không có đường đi và không còn ô ẩn nào để mở -> Thất bại
            logger.log("[Thất bại] Bảng không còn ô ẩn nhưng không tìm được cặp để nối tiếp.", state=GameState(visible_board.clone()))
            return logger.finalize(False, actions_taken, [], len(actions_taken))
            
    logger.log(f"[Xong] Giải quyết xong bằng {len(actions_taken)} nước đi!", state=GameState(visible_board.clone()))
    return logger.finalize(True, actions_taken, [], len(actions_taken))
