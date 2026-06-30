import sys
import os

from game.state import make_initial_state
from algorithms.UninformedSearchAlgorithms.bfs import bfs
from algorithms.UninformedSearchAlgorithms.dfs import dfs
from algorithms.InformedSearchAlgorithms.astar import astar
from algorithms.InformedSearchAlgorithms.greedy import greedy
from algorithms.LocalSearch.local_beam import local_beam_search
from algorithms.LocalSearch.hill_climbing import hill_climbing_search
from algorithms.ConstraintSatisfactionProblems.backtracking import backtracking_search
from algorithms.ConstraintSatisfactionProblems.forwardchecking import forwardchecking_search
from algorithms.SearchingInComplexEnvironments.partial_observable import partial_observable_search
from algorithms.SearchingInComplexEnvironments.and_or import and_or_search

def run_tests():
    print("=== BẮT ĐẦU KIỂM TRA CÁC GIẢI THUẬT ===")
    
    # Danh sách các thuật toán và hàm tương ứng
    algos = [
        ("BFS", lambda s: bfs(s)),
        ("DFS", lambda s: dfs(s)),
        ("A*", lambda s: astar(s)),
        ("Greedy", lambda s: greedy(s)),
        ("Local Beam", lambda s: local_beam_search(s)),
        ("Hill Climbing", lambda s: hill_climbing_search(s)),
        ("Backtracking (CSP)", lambda s: backtracking_search(s)),
        ("Forward Checking (CSP)", lambda s: forwardchecking_search(s)),
        ("Partial Observable", lambda s: partial_observable_search(s)),
        ("AND-OR Search", lambda s: and_or_search(s))
    ]
    
    seeds = [46, 42]
    
    for seed in seeds:
        print(f"\n--- Chạy với Seed: {seed} ---")
        for name, func in algos:
            state = make_initial_state(rows=6, cols=6, seed=seed)
            try:
                result = func(state)
                success = result.success
                steps_count = len(result.search_steps)
                
                # Kiểm tra xem bước cuối cùng (nếu thành công) có snapshot khác None hay không
                last_snapshot_ok = "N/A"
                if success and steps_count > 0:
                    last_snap, last_msg = result.search_steps[-1]
                    last_snapshot_ok = "OK" if last_snap is not None else "ERROR (None)"
                
                print(f"[{name}] Thành công: {success} | Số bước log: {steps_count} | Bản chụp bước cuối: {last_snapshot_ok}")
            except Exception as e:
                print(f"[{name}] LỖI KHI CHẠY: {e}")
                import traceback
                traceback.print_exc()

if __name__ == "__main__":
    run_tests()
