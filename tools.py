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
    step[0] += 1
    print('\033[36mSTEP\033[0m:', step[0])
    for line in chesses:
        for chess in line:
            if chess is None:
                print('〇', end='')
            elif chess.name in '将士象马车炮卒':
                print(f'\033[32m{chess.name}\033[0m', end='')
            else:
                print(f'\033[31m{chess.name}\033[0m', end='')
        print()
    print()
