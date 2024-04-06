"""min-max search"""

import dataclasses
import math
import random
import typing

type Coordinate = tuple[int, int]
"""the coordinate of chess"""

type Operation = tuple[Coordinate, Coordinate] | None
"""a valid operation"""

type ID = typing.Literal[
    -8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8]
"""all ids of chesses"""


SCORE_TABLE: dict[ID, float] = {
    0: 0,  # 空
    1: 1000,  # 帅
    2: 4,  # 仕
    3: 4,  # 相
    4: 3,  # 兵
    5: 5,  # 过河兵
    6: 9,  # 馬
    7: 10,  # 砲
    8: 18,  # 車
    -1: -1000,  # 将
    -2: -4,  # 士
    -3: -4,  # 象
    -4: -3,  # 卒
    -5: -5,  # 过河卒
    -6: -9,  # 马
    -7: -10,  # 炮
    -8: -18,  # 车
}
"""score of each chess"""


@dataclasses.dataclass
class Node:
    """Node of the min-max searching tree"""

    score: float
    operation: Operation = None


def evaluate(data: list[list[int]], score: float = 0) -> float:
    """get an evaluate score of the board data"""
    for lines in data:
        for item in lines:
            score += SCORE_TABLE[item]
    return score


def valid_coordinate(data: list[list[int]], reverse: bool = False) -> list[Coordinate]:
    """get all valid coordinates on board"""
    valid_coordinates: list[Coordinate] = []
    judge_function: typing.Callable[[int], bool] = (
        lambda x: x < 0) if reverse else (lambda x: x > 0)
    for i in range(10):
        for j in range(9):
            if judge_function(data[i][j]):
                valid_coordinates.append((i, j))
    return valid_coordinates


def valid_operation(data: list[list[int]], operation: Operation) -> tuple[bool, typing.Any]:
    """judge whether the operation is valid"""
    (si, sj), (ei, ej) = operation
    reverse = data[si][sj] < 0
    key_id = -1 if reverse else 1  # 我方将帅 ID
    sv, ev = data[si][sj], data[ei][ej]
    operate(data, si, sj, ei, ej)
    valid_coordinates = valid_coordinate(data, not reverse)  # 对方走法
    valid_coordinates = filter(lambda c: abs(
        data[c[0]][c[1]]) >= 5, valid_coordinates)  # 只考虑攻击性棋子
    for coordinate in valid_coordinates:
        for destination in possible_destination(data, *coordinate):
            if data[destination[0]][destination[1]] == key_id:  # 我方将帅在对方攻击范围内
                return False, recover(data, si, sj, ei, ej, sv, ev)
    # NOTE: “白脸将”特殊情况处理
    for i in range(3):
        for j in range(3, 5+1):
            if data[i][j] == -1:  # 发现“将”，位置 (i, j)
                for ni in range(i+1, 10):
                    if data[ni][j] == 0:
                        continue
                    elif data[ni][j] == 1:
                        return False, recover(data, si, sj, ei, ej, sv, ev)
                    else:
                        break
    return True, recover(data, si, sj, ei, ej, sv, ev)


def possible_destination(data: list[list[int]], i: int, j: int) -> list[Coordinate]:
    """get all possible destination of chess"""
    possible_destinations: list[Coordinate] = []
    match abs(id := data[i][j]):
        case 1:  # 将帅
            for di, dj in (0, 1), (0, -1), (1, 0), (-1, 0):
                ni, nj = i + di, j + dj
                if (0 <= ni <= 2 or 7 <= ni <= 9) and 3 <= nj <= 5:  # 位置判定
                    if id * data[ni][nj] <= 0:  # 规则判定
                        possible_destinations.append((ni, nj))
            # NOTE: “白脸将”特判在合法性判定中
        case 2:  # 士仕
            for di, dj in (-1, -1), (-1, 1), (1, 1), (1, -1):
                ni, nj = i + di, j + dj
                if (0 <= ni <= 2 or 7 <= ni <= 9) and 3 <= nj <= 5:  # 位置判定
                    if id * data[ni][nj] <= 0:  # 规则判定
                        possible_destinations.append((ni, nj))
        case 3:  # 象相
            for di, dj in (-2, -2), (-2, 2), (2, 2), (2, -2):
                ni, nj = i + di, j + dj
                if ni in (0, 2, 4, 5, 7, 9) and 0 <= nj <= 8:  # 位置判定
                    if id * data[ni][nj] <= 0:  # 规则判定
                        if data[(ni+i)//2][(nj+j)//2] == 0:  # 撇腿判定
                            possible_destinations.append((ni, nj))
        case 4:  # 卒兵
            di, dj = (1 if id < 0 else -1, 0)
            ni, nj = i + di, j + dj
            # NOTE: 无位置判定，过河会转变类型
            if id * data[ni][nj] <= 0:  # 规则判定
                possible_destinations.append((ni, nj))
        case 5:  # 卒兵（过河）
            for di, dj in (1 if id < 0 else -1, 0), (0, 1), (0, -1):
                ni, nj = i + di, j + dj
                if 0 <= ni <= 9 and 0 <= nj <= 8:  # 位置判定
                    if id * data[ni][nj] <= 0:  # 规则判定
                        possible_destinations.append((ni, nj))
        case 6:  # 马馬
            for di, dj in (1, 2), (1, -2), (-1, 2), (-1, -2), (2, 1), (2, -1), (-2, 1), (-2, -1):
                ni, nj = i + di, j + dj
                if 0 <= ni <= 9 and 0 <= nj <= 8:  # 位置判定
                    if id * data[ni][nj] <= 0:  # 规则判定
                        if data[round(i+di/3)][round(j+dj/3)] == 0:  # 撇腿判定
                            possible_destinations.append((ni, nj))
        case 7:  # 炮砲
            for lines in (range(1, 10), (0,)*9), (range(-1, -10, -1), (0,)*9), ((0,)*8, range(1, 9)), ((0,)*8, range(-1, -9, -1)):
                stepping_stone: bool = False
                for di, dj in zip(*lines):
                    ni, nj = i + di, j + dj
                    if 0 <= ni <= 9 and 0 <= nj <= 8:  # 位置判定（纵向）
                        if stepping_stone:  # 有垫脚石
                            if (key := id * data[ni][nj]) != 0:
                                if key < 0:  # 敌方棋子
                                    possible_destinations.append((ni, nj))
                                    break
                                else:  # 我方棋子
                                    break
                        else:  # 无垫脚石
                            if id * data[ni][nj] != 0:
                                stepping_stone = True
                            else:  # 空位
                                possible_destinations.append((ni, nj))
        case 8:  # 车車
            for lines in (range(1, 10), (0,)*9), (range(-1, -10, -1), (0,)*9), ((0,)*8, range(1, 9)), ((0,)*8, range(-1, -9, -1)):
                for di, dj in zip(*lines):
                    ni, nj = i + di, j + dj
                    if 0 <= ni <= 9 and 0 <= nj <= 8:  # 位置判定（纵向）
                        if id * data[ni][nj] == 0:  # 规则判定
                            possible_destinations.append((ni, nj))
                        elif id * data[ni][nj] < 0:
                            possible_destinations.append((ni, nj))
                            break
                        else:
                            break
        case _:
            raise ValueError(id)
    return possible_destinations


def get_operations(data: list[list[int]], reverse: bool = False) -> list[Operation]:
    """get all operations"""
    valid_operations: list[Operation] = []
    valid_coordinates = valid_coordinate(data, reverse)
    for coordinate in valid_coordinates:
        for destination in possible_destination(data, *coordinate):
            if valid_operation(data, operation := (coordinate, destination))[0]:
                valid_operations.append(operation)
    return valid_operations


def operate(data: list[list[int]], si: int, sj: int, ei: int, ej: int) -> None:
    """change the data of board"""
    data[si][sj], data[ei][ej] = 0, data[si][sj]
    if data[ei][ej] == -4 and ei >= 5:  # 卒兵过河类型转变
        data[ei][ej] = -5
    elif data[ei][ej] == 4 and ei <= 4:
        data[ei][ej] = 5


def recover(data: list[list[int]], si: int, sj: int, ei: int, ej: int, sv: int, ev: int) -> None:
    """recover the data of board after operating"""
    data[si][sj], data[ei][ej] = sv, ev


def update(node: Node, child: Node, op: Operation, ops: list[Operation], reverse: bool = False) -> None:
    """update the data of node"""
    temp = node.score
    if reverse:
        node.score = min(node.score, child.score)
    else:
        node.score = max(node.score, child.score)
    if node.score != temp:
        node.operation = op
        ops.clear()
        ops.append(op)


def min_max_search(data: list[list[int]], depth: int, *, reverse: bool = False) -> Node:
    """min value and max value search"""
    if depth == 0:
        return Node(evaluate(data))
    node: Node = Node(math.inf if reverse else -math.inf)
    ops: list[Operation] = []  # TODO
    for op in (operations := get_operations(data, reverse)):
        (si, sj), (ei, ej) = op
        sv, ev = data[si][sj], data[ei][ej]
        operate(data, si, sj, ei, ej)
        child = min_max_search(data, depth-1, reverse=not reverse)
        update(node, child, op, ops, reverse)
        recover(data, si, sj, ei, ej, sv, ev)
    if not operations:
        return Node(evaluate(data))
    node.operation = random.choice(ops)  # TODO
    return node
