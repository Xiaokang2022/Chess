"""alpha-beta search"""

import dataclasses
import math
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
    1: 100,  # 帅
    2: 3,  # 仕
    3: 3,  # 相
    4: 1,  # 兵
    5: 2,  # 过河兵
    6: 5,  # 馬
    7: 6,  # 砲
    8: 12,  # 車
    -1: -100,  # 将
    -2: -3,  # 士
    -3: -3,  # 象
    -4: -1,  # 卒
    -5: -2,  # 过河卒
    -6: -5,  # 马
    -7: -6,  # 炮
    -8: -12,  # 车
}
"""score of each chess"""


DELTA: dict[int, tuple] = {
    1: ((0, 1), (0, -1), (1, 0), (-1, 0)),
    2: ((-1, -1), (-1, 1), (1, 1), (1, -1)),
    3: ((-2, -2), (-2, 2), (2, 2), (2, -2)),
    6: ((1, 2), (1, -2), (-1, 2), (-1, -2), (2, 1), (2, -1), (-2, 1), (-2, -1)),
    7: ((range(1, 10), (0,)*9), (range(-1, -10, -1), (0,)*9), ((0,)*8, range(1, 9)), ((0,)*8, range(-1, -9, -1))),
}


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


def valid_coordinate(data: list[list[int]], reverse: bool = False, *, filter_id: int = 0) -> list[Coordinate]:
    """get all valid coordinates on board"""
    judge_function: typing.Callable[[int], bool] = (
        lambda x: x < -filter_id) if reverse else (lambda x: x > filter_id)
    valid_coordinates: list[Coordinate] = [
        (i, j)
        for i in range(10)
        for j in range(9)
        if judge_function(data[i][j])]
    # NOTE: 排序优化，更快剪枝：优先扩展攻击性强的棋子的节点
    # valid_coordinates.sort(key=lambda x: -abs(data[x[0]][x[1]]))
    return valid_coordinates


def valid_operation(data: list[list[int]], operation: Operation, *, attack: bool = True) -> bool:
    """judge whether the operation is valid"""
    (si, sj), (ei, ej) = operation
    reverse = data[si][sj] < 0
    key_id = -1 if reverse else 1  # 我方将帅 ID
    sv, ev = data[si][sj], data[ei][ej]
    if attack and ev == 0:
        return False
    process(data, si, sj, ei, ej)
    valid_coordinates = valid_coordinate(data, not reverse)  # 对方走法
    valid_coordinates = filter(lambda c: abs(
        data[c[0]][c[1]]) >= 5, valid_coordinates)  # 只考虑攻击性棋子
    for coordinate in valid_coordinates:
        for destination in possible_destination(data, *coordinate):
            if data[destination[0]][destination[1]] == key_id:  # 我方将帅在对方攻击范围内
                recover(data, si, sj, ei, ej, sv, ev)
                return False
    # NOTE: “白脸将”特殊情况处理
    for i in range(3):
        for j in range(3, 5+1):
            if data[i][j] == -1:  # 发现“将”，位置 (i, j)
                for ni in range(i+1, 10):
                    if data[ni][j] == 0:
                        continue
                    elif data[ni][j] == 1:
                        recover(data, si, sj, ei, ej, sv, ev)
                        return False
                    else:
                        break
    recover(data, si, sj, ei, ej, sv, ev)
    return True


def possible_destination(data: list[list[int]], i: int, j: int) -> list[Coordinate]:
    """get all possible destination of chess"""
    possible_destinations: list[Coordinate] = []

    match abs(id := data[i][j]):
        case 1:  # 将帅
            for di, dj in DELTA[1]:
                ni, nj = i + di, j + dj
                if (0 <= ni <= 2 or 7 <= ni <= 9) and 3 <= nj <= 5:  # 位置判定
                    if id * data[ni][nj] <= 0:  # 规则判定
                        possible_destinations.append((ni, nj))
            # NOTE: “白脸将”特判在合法性判定中
        case 2:  # 士仕
            for di, dj in DELTA[2]:
                ni, nj = i + di, j + dj
                if (0 <= ni <= 2 or 7 <= ni <= 9) and 3 <= nj <= 5:  # 位置判定
                    if id * data[ni][nj] <= 0:  # 规则判定
                        possible_destinations.append((ni, nj))
        case 3:  # 象相
            for di, dj in DELTA[3]:
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
            for di, dj in DELTA[6]:
                ni, nj = i + di, j + dj
                if 0 <= ni <= 9 and 0 <= nj <= 8:  # 位置判定
                    if id * data[ni][nj] <= 0:  # 规则判定
                        if data[round(i+di/3)][round(j+dj/3)] == 0:  # 撇腿判定
                            possible_destinations.append((ni, nj))
        case 7:  # 炮砲
            for lines in DELTA[7]:
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
            for lines in DELTA[7]:
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


def get_operations(data: list[list[int]], reverse: bool = False, *, attack: bool = False) -> list[Operation]:
    """get all operations"""
    valid_operations: list[Operation] = [
        (coordinate, destination)
        for coordinate in valid_coordinate(data, reverse, filter_id=6 if attack else 0)
        for destination in possible_destination(data, *coordinate)
        if valid_operation(data, (coordinate, destination), attack=attack)
    ]
    return valid_operations


def process(data: list[list[int]], si: int, sj: int, ei: int, ej: int) -> None:
    """change the data of board"""
    data[si][sj], data[ei][ej] = 0, data[si][sj]
    if data[ei][ej] == -4 and ei >= 5:  # 卒兵过河类型转变
        data[ei][ej] = -5
    elif data[ei][ej] == 4 and ei <= 4:
        data[ei][ej] = 5


def recover(data: list[list[int]], si: int, sj: int, ei: int, ej: int, sv: int, ev: int) -> None:
    """recover the data of board after operating"""
    data[si][sj], data[ei][ej] = sv, ev


def update(node: Node, child: Node, op: Operation, alpha: float, beta: float, reverse: bool = False) -> tuple[float, float]:
    """update the data of node"""
    temp = node.score
    if not reverse:
        alpha = node.score = max(node.score, child.score)
    else:
        beta = node.score = min(node.score, child.score)
    if node.score != temp:
        node.operation = op
    return alpha, beta


def alpha_beta_search(data: list[list[int]], depth: int, extra: int = 0, alpha: float = -math.inf, beta: float = math.inf, *, reverse: bool = False) -> Node:
    """alpha value and beta value search"""
    if depth <= -extra:
        return Node(evaluate(data))
    node: Node = Node(beta if reverse else alpha)  # 继承父节点的 α-β 值
    for op in (operations := get_operations(data, reverse, attack=depth <= 0)):
        (si, sj), (ei, ej) = op
        sv, ev = data[si][sj], data[ei][ej]
        process(data, si, sj, ei, ej)
        child = alpha_beta_search(
            data, depth-1, extra + 1 if depth == 1 and abs(sv) >= 6 and abs(ev) >= 6 else extra, alpha, beta, reverse=not reverse)
        alpha, beta = update(node, child, op, alpha, beta, reverse)
        recover(data, si, sj, ei, ej, sv, ev)
        if alpha >= beta:  # 剪枝
            break
    if not operations:
        return Node(evaluate(data))
    return node


if __name__ == "__main__":
    import time
    data = [
        [-8, -6, -3, -2, -1, -2, -3, -6, -8],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, -7, 0, 0, 0, 0, 0, -7, 0],
        [-4, 0, -4, 0, -4, 0, -4, 0, -4],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [4, 0, 4, 0, 4, 0, 4, 0, 4],
        [0, 7, 0, 0, 0, 0, 0, 7, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [8, 6, 3, 2, 1, 2, 3, 6, 8]
    ]

    t = time.time()
    node = alpha_beta_search(data, 4, reverse=True)
    print('Time:', time.time() - t)

    print('Score:', node.score)
    print('Operation: ', *node.operation)
