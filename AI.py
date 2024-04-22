"""
电脑算法
"""

import ctypes
from random import choice

import alpha_beta_search
import min_max_search
import rule
from configure import config
from constants import EXIST_DICT
from rule import rule
from tools import virtual

# def intelligence(chesses: list[list], color: str, depth: int) -> tuple[tuple[tuple[int, int], tuple[bool, int, int]] | None, int]:
#     """ 电脑算法 """
#     if not depth:  # 迭代终止条件
#         return None, 0

#     steps = {}
#     color_ = '#FF0000' if color == '#000000' else '#000000'
#     depth_ = depth-1

#     for line in chesses:
#         for chess in line:
#             if chess and chess.color == color:
#                 for step in rule(chesses, chess, True):
#                     key = (chess.x, chess.y), step
#                     steps[key] = EXIST_DICT[chesses[chess.y+step[2]]
#                                             [chess.x+step[1]].name] if step[0] else 0
#                     step_, score = virtual(
#                         chesses, chess, step, intelligence, color_, depth_)
#                     if step_:
#                         steps[key] -= score

#     if steps:
#         steps = sorted(steps.items(), key=lambda dic: dic[1], reverse=True)
#         ind = 0
#         for i, step in enumerate(steps):
#             if step[1] != steps[0][1]:
#                 break
#             ind = i
#         return choice(steps[:ind+1])

#     return None, 0


id: dict[str, int] = {
    '将': -1,
    '士': -2,
    '象': -3,
    '卒': -4,
    '马': -6,
    '炮': -7,
    '车': -8,
    '帥': 1,
    '仕': 2,
    '相': 3,
    '兵': 4,
    '馬': 6,
    '砲': 7,
    '車': 8,
}


def _lst_to_array(data: list[list[int]]) -> ctypes.Array[ctypes.Array[ctypes.c_int]]:
    """Python 二维棋局列表转换为 C 二维数组"""
    arr = (ctypes.c_int * 9 * 10)()
    for i in range(10):
        for j in range(9):
            arr[i][j] = data[i][j]
    return arr


def choose_algo(data: list[list[int]], depth: int, reverse: bool) -> alpha_beta_search.Node:
    """"""
    match config["algo"]:
        case 1:
            # 极小极大搜索算法
            node = min_max_search.min_max_search(
                data, depth, reverse=reverse)
        case 2:
            # α-β 剪枝算法
            node = alpha_beta_search.alpha_beta_search(
                data, depth, reverse=reverse)
        case _:
            # α-β 剪枝算法（C++ 实现）
            node = alpha_beta_search.Node(
                ctypes.WinDLL('./PyDLL.dll').search(
                    _lst_to_array(data), depth, (result := (ctypes.c_int * 4)()), reverse),
                ((result[0], result[1]), (result[2], result[3])))

    if node.operation[0][0] == -1:
        node.operation = None
    return node


def intelligence(chesses: list[list], color: str, depth: int) -> tuple[tuple[tuple[int, int], tuple[bool, int, int]] | None, int]:
    """"""
    data = [[0]*9 for _ in range(10)]
    for i, lines in enumerate(chesses):
        for j, chess in enumerate(lines):
            if chess is not None:
                data[i][j] = id[chess.name]
                if data[i][j] == -4 and i >= 5:  # 卒兵过河类型转变
                    data[i][j] = -5
                elif data[i][j] == 4 and i <= 4:
                    data[i][j] = 5

    node = choose_algo(data, depth, color != "#FF0000")

    if node.operation is None:
        return None, node.score
    (ci, cj), (ti, tj) = node.operation
    flag = data[ti][tj] != 0
    ti -= ci
    tj -= cj
    return ((cj, ci), (flag, tj, ti)), node.score
