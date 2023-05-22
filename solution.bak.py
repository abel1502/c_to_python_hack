# region imports
from __future__ import annotations
import typing
import sys
# import pickle
# import gc
import ctypes
import mmap

import numpy as np
from numpy.ctypeslib import ndpointer
# import numba
# endregion


# region sytem tweaks
# sys.setrecursionlimit(10 ** 5)
# gc.disable()
# endregion


# region complaints
# Placing everything in the same local scope is an optimization,
# and so is using raw functions instead of classes and methods
# (since Python optimizes locals lookup, and member lookup actually takes something like thrice the time).
# This is one of the reasons why I hate competitive programming so much.
# endregion


def main():
    # region fast io
    def input_ints() -> typing.Generator[int, None, None]:
        data = sys.stdin.readlines()
        for line in data:
            for num in line.split():
                yield int(num)

    inputs = iter(list(input_ints()))

    print = lambda what: sys.stdout.write(str(what) + '\n')
    # endregion


    # region global task params
    nodes_cnt: int
    ops_cnt: int
    nodes_cnt, ops_cnt = next(inputs), next(inputs)
    # endregion


    # region dsu
    dsu_parents: np.ndarray['nodes_cnt', np.int32] = np.arange(nodes_cnt, dtype=np.int32)
    dsu_items: np.ndarray['nodes_cnt', np.object_] = np.empty(nodes_cnt, dtype=np.object_)
    dsu_items_lens: np.ndarray['nodes_cnt', np.int32] = np.ones(nodes_cnt, dtype=np.int32)
    def _tmp(i: int):
        arr = np.empty(32, dtype=np.int32)
        arr[0] = i
        return arr
    dsu_items[:] = [_tmp(i) for i in range(nodes_cnt)]
    del _tmp


    def dsu_root(node: int) -> int:
        if dsu_parents[node] == node:
            return node
        
        root: int = dsu_root(dsu_parents[node])
        dsu_parents[node] = root
        return root


    def dsu_join(node_a: int, node_b: int) -> tuple[int, int, int, int]:
        """
        Returns the original nodes and their roots. The ones for the larger tree are returned first.
        """
        
        root_a: int = dsu_root(node_a)
        root_b: int = dsu_root(node_b)
        
        if root_a == root_b:
            return node_a, node_b, root_a, root_b
        
        if dsu_items_lens[root_a] < dsu_items_lens[root_b]:
            node_a, node_b = node_b, node_a
            root_a, root_b = root_b, root_a
        
        dsu_parents[root_b] = root_a
        
        items_a = dsu_items[root_a]
        items_b = dsu_items[root_b]
        needed_size = dsu_items_lens[root_a] + dsu_items_lens[root_b]
        while len(items_a) < needed_size:
            try:
                items_a.resize(len(items_a) * 2, refcheck=False)
            except:
                exit()
        items_a[dsu_items_lens[root_a]:needed_size] = items_b[:dsu_items_lens[root_b]]
        dsu_items_lens[root_a] = needed_size
        dsu_items[root_b] = None
        dsu_items_lens[root_b] = 0
        
        return node_a, node_b, root_a, root_b
    # endregion


    # region task api
    LOG_NODES_CNT: typing.Final[int] = 20

    depths: np.ndarray['nodes_cnt', np.int32] = np.zeros(nodes_cnt, dtype=np.int32)
    costs: np.ndarray['LOG_NODES_CNT,nodes_cnt', np.int64] = np.zeros((LOG_NODES_CNT, nodes_cnt), dtype=np.int64)
    nexts: np.ndarray['LOG_NODES_CNT,nodes_cnt', np.int32] = -np.ones((LOG_NODES_CNT, nodes_cnt), dtype=np.int32)
    neighbours: list[list[tuple[int, int]]] = [[] for _ in range(nodes_cnt)]


    def _dfs_init(parent: int, node: int, cost: int) -> None:
        depths[node] = depths[parent] + 1
        nexts[0, node] = parent
        costs[0, node] = cost
        
        for neighbour, new_cost in neighbours[node]:
            if neighbour == parent:
                continue
            
            _dfs_init(node, neighbour, new_cost)


    # @numba.njit('void(int32[:, :], int64[:, :], int32[:])', parallel=True, nogil=True)
    def _update_nexts_costs(nexts: np.ndarray, costs: np.ndarray, nodes: np.ndarray) -> None:
        for level in range(1, LOG_NODES_CNT):
            # for node_idx in numba.prange(len(nodes)):
            for node_idx in range(len(nodes)):
                node = nodes[node_idx]
                
                prev_node = nexts[level - 1, node]
                
                if prev_node == -1:
                    nexts[level, node] = -1
                    continue
                
                nexts[level, node] = nexts[level - 1, prev_node]
                costs[level, node] = costs[level - 1, node] + costs[level - 1, prev_node]

    # builtins.print(pickle.dumps(_update_nexts_costs))
    # exit()
    # _update_nexts_costs = pickle.loads(b'')

    # _func_code: bytes = (
    #     b'M\x85\xc0\x0f\x84\x85\x00\x00\x00AVI\x89\xd3N\x8d\x14\x82E1\xc9AUATU\xbd\x13'
    #     b'\x00\x00\x00SH\x89\xcb\x0f\x1fD\x00\x00M\x89\xc8L\x89\xd9I\x01\xd9\xeb%\x0f'
    #     b'\x1fD\x00\x00L\x01\xc0H\x83\xc1\x04D\x8b4\x87H\x8b\x04\xc6J\x03\x04\xe6E'
    #     b'\x89u\x00H\x89\x04\xd6I9\xcat(Hc\x11N\x8d$\x02L\x01\xcaJc\x04\xa7L\x8d'
    #     b',\x97\x83\xf8\xffu\xc9H\x83\xc1\x04A\xc7E\x00\xff\xff\xff\xffI9\xcau\xd8'
    #     b'\x83\xed\x01u\xa3[]A\\A]A^\xc3\xc3'
    # )

    # assert len(_func_code) <= mmap.PAGESIZE
    
    # _func_buf = mmap.mmap(-1, mmap.PAGESIZE, prot=mmap.PROT_READ | mmap.PROT_WRITE | mmap.PROT_EXEC)
    # _func_buf.write(_func_code)
    # _func_ptr = ctypes.c_void_p.from_buffer(_func_buf)
    # _func_type = ctypes.CFUNCTYPE(
    #     None,
    #     ndpointer(ctypes.c_int32, flags="C,W,O"),
    #     ndpointer(ctypes.c_int64, flags="C,W,O"),
    #     ndpointer(ctypes.c_int32, flags="C"),
    #     ctypes.c_size_t,
    #     ctypes.c_size_t
    # )
    # _func = _func_type(ctypes.addressof(_func_ptr))


    # def _update_nexts_costs(nexts: np.ndarray, costs: np.ndarray, nodes: np.ndarray, len_nodes: int) -> None:
    #     _func(nexts, costs, nodes, nodes_cnt, len_nodes)


    def add_edge(node_a: int, node_b: int, cost: int) -> None:
        root_a: int
        root_b: int
        node_a, node_b, root_a, root_b = dsu_join(node_a, node_b)
        
        _dfs_init(node_a, node_b, cost)
        
        neighbours[node_a].append((node_b, cost))
        neighbours[node_b].append((node_a, cost))
        
        _update_nexts_costs(nexts, costs, dsu_items[root_a], dsu_items_lens[root_a])


    def eval_path(node_a: int, node_b: int) -> int:
        if dsu_root(node_a) != dsu_root(node_b):
            return -1
        
        cost: int = 0
        
        if depths[node_a] < depths[node_b]:
            node_a, node_b = node_b, node_a
        
        if depths[node_a] != depths[node_b]:
            delta: int = depths[node_a] - depths[node_b]
            
            for level in range(LOG_NODES_CNT):
                if (delta >> level) & 1:
                    cost += costs[level, node_a]
                    node_a = nexts[level, node_a]
                    assert node_a != -1
        
        if node_a == node_b:
            return cost
        
        for level in range(LOG_NODES_CNT - 1, -1, -1):
            if nexts[level, node_a] == nexts[level, node_b] or nexts[level, node_a] == -1 or nexts[level, node_b] == -1:
                continue
            
            cost += costs[level, node_a] + costs[level, node_b]
            node_a = nexts[level, node_a]
            node_b = nexts[level, node_b]
        
        return cost + costs[0, node_a] + costs[0, node_b]
    # endregion


    # region main
    ans: int = 0

    for _ in range(ops_cnt):
        op: int = next(inputs)
        
        i, j = next(inputs), next(inputs)
        i = (i + ans) % nodes_cnt
        j = (j + ans) % nodes_cnt
        
        if op == 1:
            cost: int = next(inputs)
            # print("add_edge", i, j, cost)
            add_edge(i, j, cost)
        elif op == 2:
            # print("eval_path", i, j)
            ans = eval_path(i, j)
            print(ans)
        
        # print(">", dsu_parents, depths)
        # print(nexts)
        # print(costs)
    # endregion


if __name__ == "__main__":
    main()
