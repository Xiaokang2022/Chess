"""
电脑算法
"""

from random import choice

from constants import EXIST_DICT
from configure import config
from rule import rule
from tools import virtual


def intelligence(chesses: list[list], color: str, depth: int) -> tuple[tuple[tuple[int, int], tuple[bool, int, int]], int] | None:
    """ 电脑算法 """
    if not depth:  # 迭代终止条件
        return None, 0

    steps = {}
    color_ = '#FF0000' if color == '#000000' else '#000000'
    depth_ = depth-1

    for line in chesses:
        for chess in line:
            if chess and chess.color == color:
                for step in rule(chesses, chess, True):
                    key = (chess.x, chess.y), step
                    steps[key] = EXIST_DICT[chesses[chess.y+step[2]]
                                            [chess.x+step[1]].name] if step[0] else 0
                    step_, score = virtual(
                        chesses, chess, step, intelligence, color_, depth_)
                    if step_:
                        steps[key] -= score

    if steps:
        steps = sorted(steps.items(), key=lambda dic: dic[1], reverse=True)
        ind = 0
        for i, step in enumerate(steps):
            if step[1] != steps[0][1]:
                break
            ind = i
        return choice(steps[:ind+1])

    return None, 0

    # for line in chesses:
    #     for chess in line:
    #         if chess and chess.color == color:
    #             temp = {}

    #             for step in rule.rule(chesses, chess, True):
    #                 key = (chess.x, chess.y), step
    #                 if step[0]:
    #                     temp[key] = EXIST_DICT[chesses[chess.y+step[2]]
    #                                            [chess.x+step[1]].name]
    #                 else:
    #                     temp[key] = 0

    #             for key, _ in sorted(temp.items(), key=lambda x: x[1], reverse=True)[:depth]:
    #                 step_, score = virtual(
    #                     chesses, chess, key[1], intelligence, color_, depth_)
    #                 if step_:
    #                     temp[key] -= score

    #             steps_.update(temp)

    # chesses_ = [chess
    #             for line in chesses
    #             for chess in line
    #             if chess and chess.color == color
    #             ].sort(key=lambda x: MOVE_DICT[x.name], reverse=True)

    # for chess in chesses_:
    #     for step in rule.rule(chesses, chess, True):
    #         key = (chess.x, chess.y), step
    #         steps[key] = EXIST_DICT[
    #             chesses[chess.y+step[2]][chess.x+step[1]].name] if step[0] else 0
    #         step_, score = virtual(
    #             chesses, chess, step, intelligence, color_, depth_)
    #         if step_:
    #             steps[key] -= score


# def virtual(chesses: list[list[GUI.Chess | None]], x: int, y: int, step: list[bool, int, int], func, *args):
#     """ 模拟操作 """
#     chesses[y][x].x += step[1]
#     chesses[y][x].y += step[2]
#     temp = chesses[y+step[2]][x+step[1]]
#     chesses[y+step[2]][x+step[1]], chesses[y][x] = chesses[y][x], None
#     out = func(chesses, *args)
#     chesses[y][x] = chesses[y+step[2]][x+step[1]]
#     chesses[y+step[2]][x+step[1]] = temp
#     chesses[y][x].x -= step[1]
#     chesses[y][x].y -= step[2]
#     return out


# def score(chesses: list[list[GUI.Chess | None]], chess_: GUI.Chess) -> tuple[list[int], list[int]]:
#     """ 分数计算 """
#     red, black = [0, 0, 0], [0, 0, 0]  # 存在分，位置分，移动分

#     for line in chesses:
#         for chess in line:
#             if chess:
#                 if chess.color == '#FF0000':
#                     red[0] += EXIST_DICT[chess.name]  # 存在分计算
#                     if chess.y <= 5:  # 位置分计算
#                         red[1] += POS_LIST[chess.y][chess.x]
#                     # for step in rule.rule(chesses, chess, True):  # 攻击分计算
#                     #     if step[0]:
#                     #         red += EXIST_DICT[
#                     #             chesses[chess.y+step[2]][chess.x+step[1]].name]//2
#                 else:
#                     black[0] += EXIST_DICT[chess.name]  # 存在分计算
#                     if chess.y >= 4:  # 位置分计算
#                         black[1] += POS_LIST[chess.y][chess.x]
#                     # for step in rule.rule(chesses, chess, True):  # 攻击分计算
#                     #     if step[0]:
#                     #         black += EXIST_DICT[
#                     #             chesses[chess.y+step[2]][chess.x+step[1]].name]//2

#     if chess_.name in '帥仕相馬車砲兵':  # 计算移动分
#         red[2] += MOVE_DICT[chess_.name]
#     elif chess_.name in '将士象马车炮卒':
#         black[2] += MOVE_DICT[chess_.name]

#     return red, black


# def intelligence(chesses: list[list[GUI.Chess | None]], color: str, depth: int,
#                  ) -> tuple[tuple[tuple[int, int], tuple[bool, int, int]], int] | None:
#     """ 测试 """
#     if not depth:
#         return None, 0

#     dic, color_ = {}, '#FF0000' if color == '#000000' else '#000000'

#     for line in chesses:
#         for chess in line:
#             if chess and chess.color == color:
#                 for step in rule.rule(chesses, chess, True):
#                     red, black = virtual(
#                         chesses, chess.x, chess.y, step, score, chess)
#                     if virtual(chesses, chess.x, chess.y, step, ifgive, chess):
#                         if color == '#FF0000':
#                             red[0] -= 2000
#                         else:
#                             black[0] -= 2000
#                     if step[0] and not virtual(chesses, chess.x, chess.y, step, swap, chess, EXIST_DICT[chesses[chess.y+step[2]][chess.x+step[1]].name]):
#                         if color == '#FF0000':
#                             red[0] -= 2000
#                         else:
#                             black[0] -= 2000
#                     key = (chess.x, chess.y), step
#                     value_red = [red[0] - black[0], red[1], red[2]]
#                     value_black = [black[0] - red[0], black[1], black[2]]
#                     dic[key] = value_red if color == '#FF0000' else value_black

#     if not dic:
#         return None, 0

#     dic = dict(sorted(dic.items(), key=lambda x: x[1], reverse=True))

#     for key, value in dic.items():
#         step_, score_ = virtual(
#             chesses, key[0][0], key[0][1], key[1], intelligence, color_, depth-1)
#         if step_:
#             dic[key][0] += score_

#     dic = sorted(dic.items(), key=lambda x: x[1], reverse=True)

#     return dic[0][0], dic[0][1][0]


# def swap(chesses: list[list[GUI.Chess | None]], chess_: GUI.Chess, score: int, flag: bool = True) -> bool:
#     """ 换子分数（False说明亏棋） """
#     for line in chesses:
#         for chess in line:
#             if chess and chess_.color != chess.color:
#                 for step in rule.rule(chesses, chess, True):
#                     if step[0] and (chess_.x, chess_.y) == (chess.x+step[1], chess.y+step[2]):
#                         score -= EXIST_DICT[chess_.name] * (1 if flag else -1)
#                         if virtual(chesses, chess.x, chess.y, step, swap, chess, score, not flag):
#                             if score < 0:
#                                 return False
#                         else:
#                             return False
#                         break
#     return True


# def ifgive(chesses: list[list[GUI.Chess | None]], chess_: GUI.Chess) -> bool:
#     """ 是否白给（True就白给） """
#     for line in chesses:
#         for chess in line:
#             if chess and chess.color != chess_.color:
#                 for step in rule.rule(chesses, chess, True):
#                     if step[0] and (chess_.x, chess_.y) == (chess.x+step[1], chess.y+step[2]):
#                         if virtual(chesses, chess.x, chess.y, step, swap, chess, EXIST_DICT[chesses[chess.y+step[2]][chess.x+step[1]].name]):
#                             return True
#     return False


# def rule_local(chesses: list[list[GUI.Chess | None]], chess: GUI.Chess) -> list[tuple[bool, int, int]]:
#     """ 局部计算强化走棋规则 """
#     out = []
#     for step in rule.rule(chesses, chess, True):
#         if step[0]:
#             if not virtual(chesses, chess.x, chess.y, step, swap, chess, EXIST_DICT[chesses[chess.y+step[2]][chess.x+step[1]].name]):
#                 continue
#         else:
#             if virtual(chesses, chess.x, chess.y, step, ifgive, chess):
#                 continue
#         out.append(step)
#     return out


# def intelligence(chesses: list[list], color: str, depth: int, score: int = 0, alpha: int = float('-inf'), beta: int = float('inf')
#                  ) -> tuple[tuple[tuple[int, int], tuple[bool, int, int]], int] | None:
#     """ 电脑算法 """
#     if not depth:  # 迭代终止条件
#         return None, 0

#     color_ = '#FF0000' if color == '#000000' else '#000000'
#     self = (config['level'] - depth) % 2  # 是否己方
#     steps = {}  # 当前层所有的搜索结果
#     depth -= 1

#     for line in chesses:
#         for chess in line:
#             if chess and chess.color == color:
#                 for step in rule(chesses, chess, True):
#                     key = (chess.x, chess.y), step
#                     steps[key] = score  # 继承分数

#                     if step[0]:  # 吃棋
#                         name = chesses[chess.y+step[2]][chess.x+step[1]].name
#                         steps[key] += EXIST_DICT[name] if self else - \
#                             EXIST_DICT[name]

#                     step_next, score_next = virtual(
#                         chesses, chess, step, intelligence, color_, depth, steps[key], alpha, beta)

#                     if not step_next:
#                         continue

#                     if self:
#                         alpha = max(alpha, score_next)
#                         if beta <= alpha:
#                             return key, beta
#                     else:
#                         beta = min(beta, score_next)
#                         if beta <= alpha:
#                             return key, alpha

#     if steps:
#         steps = sorted(steps.items(), key=lambda dic: dic[1], reverse=True)
#         ind = 0
#         for i, step in enumerate(steps):
#             if step[1] != steps[0][1]:
#                 break
#             ind = i
#         return choice(steps[:ind+1])

#     return None, 0


# def score(chesses: list[list], color: str) -> int:
#     """ 局面分数 """
#     s = 0
#     for line in chesses:
#         for chess in line:
#             if chess:
#                 if chess.color == color:
#                     s += EXIST_DICT[chess.name]
#                 else:
#                     s -= EXIST_DICT[chess.name]
#     return s


# def intelligence(chesses: list[list], color: str, depth: int
#                  ) -> tuple[tuple[tuple[int, int], tuple[bool, int, int]], int] | None:
#     """ 电脑算法 """
#     if not depth:  # 迭代终止条件
#         return None, 0

#     self = (config['level'] - depth) % 2
#     color = '#FF0000' if color == '#000000' else '#000000'
#     depth -= 1

#     for line in chesses:
#         for chess in line:
#             if chess and chess.color != color:
#                 for step in rule(chesses, chess, True):
#                     return_out = (chess.x, chess.y), step
#                     s = score(chesses, chess)
#                     out, next_score = virtual(
#                         chesses, chess, step, intelligence, color)
