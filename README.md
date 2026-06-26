# Onet Connect Animal (Game Nối Thú)

Dự án game Nối Thú được xây dựng bằng Python và Pygame, tích hợp các thuật toán tìm kiếm và bài toán thỏa mãn ràng buộc (CSP) để tự động giải bàn cờ.

## Cấu trúc thư mục

* `main.py`: Giao diện chính của game và luồng điều khiển.
* `game/`: Chứa mã nguồn quản lý luật chơi, trạng thái game, trực quan hóa.
  * [board.py]: Quản lý bàn cờ 2D.
  * [rules.py]: Định nghĩa luật nối thú.
  * [state.py]: Định nghĩa bài toán tìm kiếm và biểu diễn trạng thái game.
  * [visualizer.py]: Xử lý đồ họa và giao diện Pygame.
* `algorithms/`: Các nhóm thuật toán giải bài toán.
  * [base.py]: Cấu trúc dữ liệu chung (`SearchResult`, `SearchLogger`).
  * `UninformedSearchAlgorithms/`: Thuật toán tìm kiếm mù (BFS, UCS,...).
  * `InformedSearchAlgorithms/`: Thuật toán tìm kiếm có thông tin (A*, Greedy,...).
  * `LocalSearch/`: Thuật toán tìm kiếm cục bộ (Hill-Climbing, Simulated Annealing,...).
  * `SearchingInComplexEnvironments/`: Thuật toán tìm kiếm trong môi trường phức tạp (AND-OR Search, Partial Observable,...).
  * `ConstraintSatisfactionProblems/`: Bài toán thỏa mãn ràng buộc (Backtracking, AC-3,...).
  * `AdversarialSearch/`: Thuật toán tìm kiếm đối kháng (Minimax, Alpha-Beta,...).

## Hướng dẫn cài đặt

1. Đảm bảo bạn đã cài đặt Python (phiên bản >= 3.8).
2. Cài đặt các thư viện cần thiết:
   ```bash
   pip install -r requirements.txt
   ```

## Hướng dẫn chạy game

Chạy file giao diện chính:
```bash
python main.py
```

## Các tính năng chính

* **Chơi thủ công:** Chọn các cặp hình thú giống nhau để nối theo luật Pikachu.
* **Chạy AI:** Chọn thuật toán mong muốn (A*, CSP,...) để xem AI tự động tìm đường giải quyết toàn bộ bàn cờ.
* **Ghi log & Phân tích:** Theo dõi từng bước mở rộng node, thời gian chạy và số lượng node đã sinh ra của mỗi thuật toán để so sánh hiệu năng.
