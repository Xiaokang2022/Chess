"""
游戏规则控制
"""

from threading import Thread
from tkinter import messagebox

from configure import config, statistic
from tools import virtual


def rule(chesses: list[list], chess, flag_: bool = False) -> list[tuple[bool, int, int]]:
    """ 返回可走位置 """
    pos: list[tuple[bool, int, int]] = []

    def ifappend(step: tuple[bool, int, int]) -> bool:
        """ 应将判定 """
        if flag_:
            color = '#FF0000' if chess.color == '#000000' else '#000000'
            if color in virtual(chesses, chess, step, warn):
                return False
        return True

    def append(x: int, y: int, flag: bool | None = None) -> None:
        """ 添加位置 """
        if flag and ifappend(step := (flag, x, y)):
            pos.append(step)
        elif chess_ := chesses[chess.y+y][chess.x+x]:
            (step := (True, x, y))
            if chess_.color != chess.color and ifappend(step):
                pos.append(step)
        elif ifappend(step := (False, x, y)):
            pos.append(step)

    if chess.name in '将帥':
        for x, y in (1, 0), (-1, 0), (0, 1), (0, -1):
            if 3 <= chess.x+x <= 5 and (0 <= chess.y+y <= 2 or 7 <= chess.y+y <= 9):
                append(x, y)
        for y in range(1, 10) if chess.y <= 2 else range(-1, -10, -1):  # 白脸将
            if 0 <= chess.y+y <= 9 and (chess_ := chesses[chess.y+y][chess.x]):
                if chess_.name in '将帥':
                    append(x, y, True)
                else:
                    break
    elif chess.name in '士仕':
        for x, y in (1, 1), (-1, -1), (1, -1), (-1, 1):
            if 3 <= chess.x+x <= 5 and (0 <= chess.y+y <= 2 or 7 <= chess.y+y <= 9):
                append(x, y)
    elif chess.name in '象相':
        for x, y in (2, 2), (-2, -2), (2, -2), (-2, 2):
            if 0 <= chess.x+x <= 8 and chess.y+y in (0, 2, 4, 5, 7, 9):
                if not chesses[(2*chess.y+y)//2][(2*chess.x+x)//2]:  # 撇腿判定
                    append(x, y)
    elif chess.name in '马馬':
        for x, y in (1, 2), (1, -2), (-1, 2), (-1, -2), (2, 1), (-2, 1), (2, -1), (-2, -1):
            if 0 <= chess.x+x <= 8 and 0 <= chess.y+y <= 9:
                if not chesses[round(chess.y+y/3)][round(chess.x+x/3)]:  # 撇腿判定
                    append(x, y)
    elif chess.name in '车車':
        for k in 9, 10:
            for line in range(1, k), range(-1, -k, -1):
                for x, y in [(0, i) if k-9 else (i, 0) for i in line if 0 <= (chess.x, chess.y)[k-9]+i <= k-1]:
                    if chess_ := chesses[chess.y+y][chess.x+x]:
                        if chess_.color != chess.color:
                            append(x, y, True)
                        break
                    else:
                        append(x, y, False)
    elif chess.name in '炮砲':
        for k in 9, 10:
            for line in range(1, k), range(-1, -k, -1):
                flag = False
                for x, y in [(0, i) if k-9 else (i, 0) for i in line if 0 <= (chess.x, chess.y)[k-9]+i <= k-1]:
                    if chess_ := chesses[chess.y+y][chess.x+x]:
                        if flag:
                            if chess_.color != chess.color:
                                append(x, y, True)
                            break
                        flag = True
                    elif not flag:
                        append(x, y, False)
    else:  # 卒兵
        flag = chess.name == '兵'
        y = -1 if flag else 1
        if 0 <= chess.y+y <= 9:
            append(0, y)
        if (chess.y+y <= 3 and flag) or (chess.y+y >= 6 and not flag):
            for x in [i for i in (-1, 1) if 0 <= chess.x+i <= 8]:
                append(x, 0)

    return pos


def warn(chesses: list[list], color: str | None = None) -> list[str]:
    """ 将军警告（接收攻击者，返回攻击者） """
    case_list: list[str] = []
    for line in chesses:
        for chess in line:
            if chess:
                if color and color != chess.color:
                    continue
                for step in rule(chesses, chess):
                    if step[0] and chesses[chess.y+step[2]][chess.x+step[1]].name in '将帥':
                        case_list.append(chess.color)
    return case_list


def peace() -> bool:
    """ 和棋判定 """
    import GUI
    if GUI.Global.count >= config['peace']*2:
        return True
    if (ind := GUI.Global.index) >= 11:
        if GUI.Global.cache[ind-3:ind+1]*2 == GUI.Global.cache[ind-11:ind-3]:
            return True
    return False


def dead(chesses: list[list], color: str) -> str | None:
    """ 绝杀判定（接收攻击者，返回攻击者） """
    for line in chesses:
        for chess in line:
            if chess and chess.color != color:
                for step in rule(chesses, chess):
                    if not virtual(chesses, chess, step, warn, color):
                        return
    return color


def gameover(color: str | None = None) -> None:
    """ 游戏结束 """
    import GUI
    GUI.Global.player = None
    GUI.Global.choose = None
    tone, win = ('恭喜你！', '赢了！') if color == '#FF0000' else ('很遗憾，', '输了。')
    who = '你'
    if not color:
        statistic(Peace=1)
        return messagebox.showinfo('游戏结束', '本局和棋！\t')
    if GUI.Global.mode in 'LOCAL TEST':
        tone, win = '', '获胜！'
        who = '红方' if color == '#FF0000' else '黑方'
    if win == '赢了！':
        statistic(Win=1)
    elif win == '输了。':
        statistic(Lose=1)
    messagebox.showinfo('游戏结束', '%s%s%s\t' % (tone, who, win))
    GUI.Window.canvas.itemconfigure(GUI.Window.timer, text='00:00\n- 中国象棋 -')


def ifop(chess, player: str) -> bool:
    """ 是否可操作 """
    import GUI
    if not GUI.Global.mode or not player:
        return False
    if GUI.Global.mode in 'COMPUTER END':
        return player == '玩家' and chess.color == '#FF0000'
    elif GUI.Global.mode == 'LAN':
        return player == '我方' and chess.color == '#FF0000'
    elif GUI.Global.mode == 'LOCAL':
        return player[0] == '红黑'[chess.color == '#000000']
    return False


def switch() -> None:
    """ 切换走棋方 """
    import GUI
    if GUI.Global.player:
        if GUI.Global.mode in 'COMPUTER END':
            GUI.Global.player = '玩家' if GUI.Global.player == '电脑' else '电脑'
        elif GUI.Global.mode == 'LAN':
            GUI.Global.player = '我方' if GUI.Global.player == '对方' else '对方'
        else:
            GUI.Global.player = '红方' if GUI.Global.player == '黑方' else '黑方'
    else:
        if GUI.Global.first:
            if GUI.Global.mode in 'LAN COMPUTER END':
                statistic(First=1)
            GUI.Global.player = '我方' if GUI.Global.mode == 'LAN' else '玩家' if GUI.Global.mode in 'COMPUTER END' else '红方'
        else:
            GUI.Global.player = '对方' if GUI.Global.mode == 'LAN' else '电脑' if GUI.Global.mode in 'COMPUTER END' else '黑方'
    GUI.Window.clock([0, None])


def gameset(code: str | None = None) -> None:
    """ 游戏设定 """
    if code:
        import GUI
        GUI.Global.first = bool(int(code[0]))
        lis = [(0, 9), (8, 9), (0, 0), (8, 0), (1, 7), (7, 7),
               (1, 2), (7, 2), (1, 9), (7, 9), (1, 0), (7, 0)]
        for i, v in enumerate(code):
            if int(v) and i:
                x, y = lis[i-1]
                GUI.Global.chesses[y][x].destroy()
                GUI.Global.chesses[y][x] = None


def modechange(mode: str, code: str | None = None) -> None:
    """ 改变模式 """
    import GUI
    if mode != 'END':
        GUI.Window.chess()
    GUI.Global.cache.clear()
    GUI.Global.index = -1
    GUI.Global.count = 0
    GUI.Global.mode = mode
    GUI.Global.choose = None
    gameset(code)
    statistic(**{'Play': 1, mode: 1})
    mode = '双人对弈' if mode == 'LOCAL' else '联机对抗' if mode == 'LAN' else '人机对战' if mode in 'COMPUTER' else '残局挑战' if mode == 'END' else 'AI测试'
    GUI.Window.root.title('中国象棋 - %s' % mode)
    GUI.Global.player = None
    GUI.Window.tip('— 提示 —\n游戏模式已更新\n为“%s”模式' % mode)
    switch()
    if GUI.Global.mode in 'COMPUTER END' and not GUI.Global.first:
        GUI.Window.root.after(
            500, Thread(target=lambda: GUI.Window.AImove('#000000'), daemon=True).start)


def revoke(flag: bool = False) -> None:
    """ 撤销（悔棋） """
    import GUI
    if flag or (GUI.Global.player and GUI.Global.mode in 'LOCAL' and GUI.Global.index >= 0):
        if GUI.Global.choose:
            GUI.Global.choose.virtual_delete()
            GUI.Global.choose.highlight(False, inside=False)
            GUI.Global.choose = None
        o, pos, v, = GUI.Global.cache[GUI.Global.index]
        m = GUI.Global.chesses[pos[1]][pos[0]]
        if o:
            color = '#FF0000' if o in '帥仕相馬車砲兵' else '#000000'
            GUI.Chess(o, *pos, color)
        else:
            GUI.Global.chesses[pos[1]][pos[0]] = None
        m.move(False, *v, True)
        GUI.Global.index -= 1
        switch()
        statistic(Revoke=1)
    elif GUI.Global.mode in 'COMPUTER END' and GUI.Global.player == '玩家' and GUI.Global.index >= 0:
        revoke(True)
        GUI.Window.root.after(600, revoke, True)
        statistic(Revoke=-1)
    else:
        GUI.Window.tip('— 提示 —\n当前模式或状态下\n无法进行悔棋操作！')
        GUI.Window.root.bell()


def recovery(flag: bool = False) -> None:
    """ 恢复（悔棋） """
    import GUI
    if flag or (GUI.Global.player and GUI.Global.mode == 'LOCAL' and -1 <= GUI.Global.index < len(GUI.Global.cache)-1):
        if GUI.Global.choose:
            GUI.Global.choose.virtual_delete()
            GUI.Global.choose.highlight(False, inside=False)
            GUI.Global.choose = None
        GUI.Global.index += 1
        o, pos, v, = GUI.Global.cache[GUI.Global.index]
        GUI.Global.chesses[pos[1] + v[1]][pos[0] + v[0]].move(
            bool(o), -v[0], -v[1], True)
        GUI.Global.chesses[pos[1] + v[1]][pos[0] + v[0]] = None
        switch()
        statistic(Recovery=1)
    elif GUI.Global.mode in 'COMPUTER END' and GUI.Global.player == '玩家' and -1 <= GUI.Global.index < len(GUI.Global.cache)-1:
        recovery(True)
        GUI.Window.root.after(600, recovery, True)
        statistic(Recovery=-1)
    else:
        GUI.Window.tip('— 提示 —\n当前模式或状态下\n无法进行撤销悔棋操作！')
        GUI.Window.root.bell()
