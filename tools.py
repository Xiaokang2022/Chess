"""
工具函数
"""


def virtual(chesses: list[list], chess, step: list[bool, int, int], function, *args):
    """ 虚拟操作 """
    chesses[chess.y][chess.x] = None
    chess.x += step[1]
    chess.y += step[2]
    temp = chesses[chess.y][chess.x]
    chesses[chess.y][chess.x] = chess
    value = function(chesses, *args)
    chesses[chess.y][chess.x] = temp
    chess.x -= step[1]
    chess.y -= step[2]
    chesses[chess.y][chess.x] = chess
    return value


def print_chess(chesses: list[list], step: list[int] = [0]) -> None:
    """ 输出当前棋局 """
    for line in chesses:
        print(''.join(getattr(chess, 'name', '〇')
              for chess in line))
    step[0] += 1
    print('STEP:', step[0])
