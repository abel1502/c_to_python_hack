from __future__ import annotations
import typing
import sys

import numpy as np
import numba
import numba.pycc


@numba.njit('void(int32[:, :], int64[:, :], int32[:], int32)', cache=True)
def _update_nexts_costs(nexts: np.ndarray, costs: np.ndarray, nodes: np.ndarray, LOG_NODES_CNT: int) -> None:
    nexts[1:, nodes] = -1
        
    for level in range(1, LOG_NODES_CNT):
        # _handle_level(nodes, level, nexts, costs)
        for node in nodes:
            prev_node = nexts[level - 1, node]
            
            if prev_node == -1:
                continue
            
            nexts[level, node] = nexts[level - 1, prev_node]
            costs[level, node] = costs[level - 1, node] + costs[level - 1, prev_node]


