"""
图形界面
"""

from json import load
from math import hypot
from os import listdir
from sys import exit
from threading import Thread
from time import time
from tkinter import Event, IntVar, Menu, filedialog, messagebox, ttk
from winsound import SND_ASYNC, PlaySound

import LAN
import rule
import tkintertools as tkt
from AI import intelligence
from configure import config, configure, statistic
from constants import (BACKGROUND, FEN, SCREEN_HEIGHT, SCREEN_WIDTH,
                       STATISTIC_DICT, VIRTUAL_BLACK, VIRTUAL_INSIDE,
                       VIRTUAL_OUTLINE, VIRTUAL_RED, VOICE_BUTTON,
                       VOICE_CHOOSE, VOICE_DROP, VOICE_EAT, VOICE_WARN, S)
from main import __author__, __update__, __version__
from tools import print_chess


class Global:
    """ 全局变量 """
    mode = None     # 当前游戏模式
    timer = 0       # 计时判断时间戳
    count = 0       # 未吃棋回合计数（和棋判定需要）
    index = -1      # 当前缓存索引
    first = None    # 当前先手方
    player = None   # 当前操作方
    choose = None   # 当前选中棋子
    cache = []      # 走棋缓存列表
    chesses = [     # 棋盘列表
        [None]*9 for _ in range(10)]  # type: list[list[Chess | None]]


class Window:
    """ 主窗口 """

    root = tkt.Tk(
        '中国象棋', int(640*S), int(710*S),
        (SCREEN_WIDTH - tkt.S * 640 * S)//2, 0, exit)
    root.resizable(False, False)
    menu = Menu(root, tearoff=False)
    root.configure(menu=menu)
    canvas = tkt.Canvas(root, 640*S, 710*S, bg=BACKGROUND)
    canvas.place(x=0, y=0)
    timer = canvas.create_text(
        320*S, 355*S, font=('楷体', int(20*S)), justify='center', text='00:00\n- 中国象棋 -')

    def __init__(self) -> None:
        """ 初始化 """
        self.init_menu()
        self.init_bind()
        self.init_board()
        self.new()
        self.root.mainloop()

    def init_menu(self) -> None:
        """ 菜单栏 """
        m1 = Menu(self.menu, tearoff=False)
        m2 = Menu(self.menu, tearoff=False)
        self.menu.add_cascade(label='选项(O)', menu=m1)
        self.menu.add_cascade(label='帮助(H)', menu=m2)
        m1.add_command(label='导入棋局', command=open_file, accelerator='Ctrl+O')
        m1.add_command(label='导出棋局', command=save_file, accelerator='Ctrl+S')
        m1.add_command(label='棋局库', command=self.library)
        m1.add_separator()
        m1.add_command(label='撤销', accelerator='Ctrl+Z', command=rule.revoke)
        m1.add_command(label='恢复', accelerator='Ctrl+Y', command=rule.recovery)
        m1.add_separator()
        m1.add_command(label='游戏设置', command=self.setting)
        m1.add_command(label='新游戏', accelerator='Ctrl+N', command=self.new)
        m1.add_command(label='退出', accelerator='Ctrl+Q', command=exit)
        m2.add_command(label='游戏说明', accelerator='Ctrl+H', command=self.help)
        m2.add_command(label='统计数据', command=self.statistic)
        m2.add_separator()
        m2.add_command(label='关于', command=about)

    def init_bind(self) -> None:
        """ 绑定 """
        self.root.bind('<Motion>', self.touch)
        self.root.bind('<Button-1>', self.choose)
        self.root.bind('<Control-h>', lambda _: self.help())        # 游戏说明
        self.root.bind('<Control-z>', lambda _: rule.revoke())      # 撤销
        self.root.bind('<Control-y>', lambda _: rule.recovery())    # 恢复
        self.root.bind('<Control-o>', lambda _: open_file())        # 打开
        self.root.bind('<Control-s>', lambda _: save_file())        # 另存为…
        self.root.bind('<Control-n>', lambda _: self.new())         # 新游戏
        self.root.bind('<Control-q>', lambda _: self.root.quit())   # 退出
        self.root.bind('<Control-t>', lambda _: self.test())        # AI测试

    def init_board(self) -> None:
        """ 棋盘 """
        def point(x: int, y: int) -> None:
            """ 关键点 """
            a, b = 5*S, 25*S  # 间距，长度
            if x != 40*S:
                self.canvas.create_line(x-b, y-a, x-a, y-a, x-a, y-b)
                self.canvas.create_line(x-a, y+b, x-a, y+a, x-b, y+a)
            if x != 600*S:
                self.canvas.create_line(x+a, y-b, x+a, y-a, x+b, y-a)
                self.canvas.create_line(x+b, y+a, x+a, y+a, x+a, y+b)

        self.canvas.create_text(
            320*S, 355*S, text='楚 河'+'\t'*2+'汉 界', font=('华文行楷', int(40*S)))

        self.canvas.create_rectangle(32*S, 32*S, 608*S, 678*S, width=3)
        self.canvas.create_rectangle(40*S, 40*S, 600*S, 670*S)
        self.canvas.create_line(250*S, 40*S, 390*S, 180*S)
        self.canvas.create_line(250*S, 530*S, 390*S, 670*S)
        self.canvas.create_line(390*S, 40*S, 250*S, 180*S)
        self.canvas.create_line(390*S, 530*S, 250*S, 670*S)

        point(110*S, 180*S)
        point(530*S, 180*S)
        point(110*S, 530*S)
        point(530*S, 530*S)

        for x in 40, 180, 320, 460, 600:
            point(x*S, 250*S)
            point(x*S, 460*S)

        for x in range(7):
            _ = 110+x*70
            self.canvas.create_line(_*S, 40*S, _*S, 320*S)
            self.canvas.create_line(_*S, 390*S, _*S, 670*S)
        for y in range(8):
            _ = 110+y*70
            self.canvas.create_line(40*S, _*S, 600*S, _*S)

    def new(self) -> None:
        """ 新游戏页面 """
        m = MiniWin(self.root, '选择模式', 300, 150)
        toplevel, canvas = m.toplevel, m.canvas
        canvas.configure(bg='#FFFFFF')
        toplevel.var_list = [IntVar(toplevel, not i) for i in range(13)]

        def canvas_set(mode: str) -> None:
            """ 设定次级画布 """
            canvas_ = tkt.Canvas(
                toplevel, 300*S, 150*S, expand=False)
            canvas_.place(x=0, y=0)
            last = tkt.CanvasButton(
                canvas_, 6*S, 121*S, 80*S, 23*S, 6*S, font=('楷体', round(12*S)), text='上一步',
                command=lambda: (toplevel.title('选择模式'), canvas_.destroy()))
            last.command_ex['press'] = lambda: PlaySound(
                VOICE_BUTTON, SND_ASYNC)
            if mode in 'COMPUTER LOCAL':
                more_set(toplevel, canvas_)
                last.move(122*S, 0)
                tkt.CanvasButton(
                    canvas_, 214*S, 121*S, 80*S, 23*S, 6*S, font=('楷体', round(12*S)), text='开始',
                    command=lambda: (rule.modechange(mode, ''.join(
                        [str(v.get()) for v in toplevel.var_list])), toplevel.destroy())
                ).command_ex['press'] = lambda: PlaySound(VOICE_BUTTON, SND_ASYNC)
                toplevel.title(
                    '选择模式 - ' + ('双人对弈' if mode == 'LOCAL' else '人机对战'))
            elif mode == 'LAN':
                toplevel.title('选择模式 - 联机对抗')
                info = canvas_.create_text(
                    150*S, 85*S, font=('楷体', round(10*S)), justify='center', text='请选择连接方式')
                tkt.CanvasButton(
                    canvas_, 20*S, 20*S, 120*S, 30*S, 8*S, '客户端连接', font=('楷体', round(12*S)),
                    command=lambda: (LAN.API(toplevel, 'CLIENT'),
                                     PlaySound(VOICE_BUTTON, SND_ASYNC))
                ).command_ex['touch'] = lambda: canvas_.itemconfigure(
                    info, text='主动的连接方式\n套接字将主动搜索局域网内可识别的服务端')
                tkt.CanvasButton(
                    canvas_, 160*S, 20*S, 120*S, 30*S, 8*S, '服务端连接', font=('楷体', round(12*S)),
                    command=lambda: (LAN.API(toplevel, 'SERVER'),
                                     PlaySound(VOICE_BUTTON, SND_ASYNC))
                ).command_ex['touch'] = lambda: canvas_.itemconfigure(
                    info, text='被动的连接方式\n套接字将惰性地等待可能的客户端的连接')

        tkt.CanvasButton(
            canvas, 25*S, 15*S, 70*S, 70*S, 10*S, 'AI', font=('方正舒体', round(50*S), 'bold'),
            command=lambda: (canvas_set('COMPUTER'),
                             PlaySound(VOICE_BUTTON, SND_ASYNC))
        ).command_ex['touch'] = lambda: canvas.itemconfigure(text, text='人脑与电脑的激烈碰撞！')
        tkt.CanvasButton(
            canvas, 115*S, 15*S, 70*S, 70*S, 10*S, '将', font=('方正舒体', round(50*S), 'bold'),
            command=lambda: (canvas_set('LOCAL'),
                             PlaySound(VOICE_BUTTON, SND_ASYNC))
        ).command_ex['touch'] = lambda: canvas.itemconfigure(text, text='双方激烈对峙，到底谁能笑到最后？')
        tkt.CanvasButton(
            canvas, 205*S, 15*S, 70*S, 70*S, 10*S, '帥', font=('方正舒体', round(50*S), 'bold'),
            command=lambda: (canvas_set('LAN'), PlaySound(
                VOICE_BUTTON, SND_ASYNC))
        ).command_ex['touch'] = lambda: canvas.itemconfigure(text, text='和局域网里的朋友一起玩耍吧！')
        canvas.create_text(60*S, 100*S, text='人机对战', font=('楷体', round(12*S)))
        canvas.create_text(150*S, 100*S, text='双人对弈', font=('楷体', round(12*S)))
        canvas.create_text(240*S, 100*S, text='联机对抗', font=('楷体', round(12*S)))
        canvas.create_rectangle(-1, 115*S, 301*S, 151*S,
                                width=0, fill='#F1F1F1')
        text = canvas.create_text(
            150*S, 132*S, text='请选择游戏模式', font=('楷体', round(12*S)))

    def help(self, _ind: list[int] = [0]) -> None:
        """ 帮助页面 """
        def text_limit(string: str, length: int) -> str:
            """ 文本单行长度限制 """
            out: str = ' '*4
            for i, s in enumerate(string):
                out += s
                if not (i+2) % length:
                    out += '\n'
            return out.rstrip()+'\n'

        def canvas_set(ind: int) -> None:
            """ 画布设定 """
            _ind[0] += ind
            canvas.itemconfigure(
                page, text='%d/%d' % (_ind[0]+1, len(data_list)))
            canvas.itemconfigure(title, text=data_list[_ind[0]][0])
            canvas.itemconfigure(text, text=data_list[_ind[0]][1])
            last.set_live(True if _ind[0] else False)
            next.set_live(True if _ind[0] < len(data_list)-1 else False)

        canvas = MiniWin(self.root, '游戏说明', 400, 300).canvas
        logo(canvas)
        canvas.create_rectangle(
            -1, 265*S, 401*S, 301*S, width=0, fill='#F1F1F1')
        canvas.create_line(10*S, 40*S, 200*S, 40*S, width=round(2*S))
        page = canvas.create_text(200*S, 282*S, font=('楷体', round(12*S)))
        title = canvas.create_text(
            10*S, 20*S, font=('楷体', round(20*S)), anchor='w')
        text = canvas.create_text(
            10*S, 50*S, anchor='nw', font=('楷体', round(12*S)))
        last = tkt.CanvasButton(
            canvas, 5*S, 270*S, 100*S, 25*S, 6*S, '< 上一页', font=('楷体', round(12*S)),
            command=lambda: canvas_set(-1))
        next = tkt.CanvasButton(
            canvas, 295*S, 270*S, 100*S, 25*S, 6*S, '下一页 >', font=('楷体', round(12*S)),
            command=lambda: canvas_set(1))
        last.command_ex['press'] = lambda: PlaySound(VOICE_BUTTON, SND_ASYNC)
        next.command_ex['press'] = lambda: PlaySound(VOICE_BUTTON, SND_ASYNC)

        data_list, ind = [], -1
        with open('help.md', 'r', encoding='utf-8') as file:
            for line in file.readlines():
                if line.startswith('###'):
                    ind += 1
                    data_list.append([line[4:].rstrip(), ''])
                else:
                    data_list[ind][1] += text_limit(line, 22)

        canvas_set(0)

    def statistic(self) -> None:
        """ 统计数据页面 """
        canvas = MiniWin(self.root, '统计数据', 400, 300).canvas
        logo(canvas)
        key_text, value_text = '', ''
        with open('statistic.json', 'r', encoding='utf-8') as data:
            for key, value in load(data).items():
                key_text += '%s:\n' % STATISTIC_DICT[key]
                value_text += '%d\n' % value
        canvas.create_text(
            20*S, 4*S, text=key_text, font=('楷体', round(12*S)), anchor='nw')
        canvas.create_text(
            380*S, 4*S, text=value_text, font=('楷体', round(12*S)), anchor='ne', justify='right')

    def setting(self) -> None:
        """ 设置页面 """
        def save() -> None:
            """ 保存设定 """
            configure(
                scale=float(scale.get()),
                virtual=eval(info.value),
                auto_scale=eval(auto_scale.value),
                level=int(level.get()),
                peace=int(peace.get()),
                algo=1 if ai.value == "极小极大搜索" else 2 if ai.value == "alpha-beta 剪枝" else 0)
            toplevel.destroy()

        def default() -> None:
            """ 默认设定 """
            scale.set('1')
            scale.cursor_flash()
            level.set('2')
            level.cursor_flash()
            peace.set('60')
            peace.cursor_flash()
            info.configure(text='True')
            auto_scale.configure(text='True')
            ai.configure(text="alpha-beta 剪枝(C++实现)")

        m = MiniWin(self.root, '游戏设置', 400, 300)
        toplevel, canvas = m.toplevel, m.canvas
        logo(canvas)
        canvas.create_rectangle(
            -1, 265*S, 401*S, 301*S, width=0, fill='#F1F1F1')
        canvas.create_text(
            20*S, 20*S, text='窗口缩放系数（重启生效）', font=('楷体', round(12*S)), anchor='w')
        canvas.create_text(
            20*S, 50*S, text='窗口自动缩放（重启生效）', font=('楷体', round(12*S)), anchor='w')
        canvas.create_text(
            20*S, 80*S, text='棋子可走显示', font=('楷体', round(12*S)), anchor='w')
        canvas.create_text(
            20*S, 110*S, text='AI最大搜索深度', font=('楷体', round(12*S)), anchor='w')
        canvas.create_text(
            20*S, 140*S, text='AI搜索算法', font=('楷体', round(12*S)), anchor='w')
        canvas.create_text(
            20*S, 170*S, text='和棋判定回合数', font=('楷体', round(12*S)), anchor='w')

        scale = tkt.CanvasEntry(
            canvas, 220*S, 10*S, 100*S, 20*S, 5*S, justify='center', font=('楷体', round(12*S)),
            color_fill=tkt.COLOR_NONE)
        scale.set(str(config['scale']))
        scale.cursor_flash()
        auto_scale = tkt.CanvasButton(
            canvas, 220*S, 40*S, 80*S, 20*S, 5*S, str(config['auto_scale']), font=('楷体', round(12*S)),
            command=lambda: auto_scale.configure(
                text='True' if auto_scale.value == 'False' else 'False'),
            color_fill=tkt.COLOR_NONE)
        auto_scale.command_ex['press'] = lambda: PlaySound(
            VOICE_BUTTON, SND_ASYNC)
        info = tkt.CanvasButton(
            canvas, 130*S, 70*S, 80*S, 20*S, 5*S, str(config['virtual']), font=('楷体', round(12*S)),
            command=lambda: info.configure(
                text='True' if info.value == 'False' else 'False'),
            color_fill=tkt.COLOR_NONE)
        info.command_ex['press'] = lambda: PlaySound(VOICE_BUTTON, SND_ASYNC)
        level = tkt.CanvasEntry(
            canvas, 140*S, 100*S, 100*S, 20*S, 5*S, justify='center', font=('楷体', round(12*S)),
            color_fill=tkt.COLOR_NONE)
        level.set(str(config['level']))
        level.cursor_flash()
        peace = tkt.CanvasEntry(
            canvas, 140*S, 160*S, 100*S, 20*S, 5*S, justify='center', font=('楷体', round(12*S)),
            color_fill=tkt.COLOR_NONE)
        peace.set(str(config['peace']))
        peace.cursor_flash()
        ai = tkt.CanvasButton(canvas, 110*S, 130*S, 200*S, 20*S, 5*S,
                              "极小极大搜索" if config[
                                  'algo'] == 1 else "alpha-beta 剪枝" if config['algo'] == 2 else "alpha-beta 剪枝(C++实现)",
                              font=('楷体', round(12*S)), color_fill=tkt.COLOR_NONE,
                              command=lambda: ai.configure(text=("极小极大搜索" if ai.value == "alpha-beta 剪枝(C++实现)" else "alpha-beta 剪枝" if ai.value == "极小极大搜索" else "alpha-beta 剪枝(C++实现)")))
        ai.command_ex['press'] = lambda: PlaySound(VOICE_BUTTON, SND_ASYNC)

        tkt.CanvasButton(canvas, 314*S, 271*S, 80*S, 23*S, 6*S, '保存', font=('楷体', round(12*S)), command=save
                         ).command_ex['press'] = lambda: PlaySound(VOICE_BUTTON, SND_ASYNC)
        tkt.CanvasButton(canvas, 228*S, 271*S, 80*S, 23*S, 6*S, '恢复默认', font=('楷体', round(12*S)), command=default
                         ).command_ex['press'] = lambda: PlaySound(VOICE_BUTTON, SND_ASYNC)

    def library(self) -> None:
        """ 棋局库 """
        def scroll(event: Event) -> None:
            """ 上下移动画布 """
            if (event.delta < 0 and content.pos <= 10) or (event.delta > 0 and content.pos >= content.length):
                return
            key = 1 if event.delta > 0 else -1
            content.pos += key
            for widget in content.widget():
                tkt.move(content, widget, 0, 35*key*S, 300, 'smooth', 30)

        def canvas_set(path: str) -> None:
            """ 画布设定 """
            if path.endswith('.fen'):
                toplevel.destroy()
                return open_file(path)
            elif path[-4:] == 'data':
                back.set_live(False)
            else:
                back.set_live(True)
            nonlocal path_
            path_ = path
            info.configure(text=path.replace('./data', '.'))
            path_list = listdir(path)
            content.pos = content.length = len(path_list)
            for widget in content.widget():
                widget.destroy()
            for i, file in enumerate(path_list):
                tkt.CanvasButton(
                    content, 5*S, (5+i*35)*S, 280*S, 30*S, 5 *
                    S, file.replace('.fen', ''),
                    command=lambda path=path, file=file: canvas_set(
                        '%s/%s' % (path, file))
                ).command_ex['press'] = lambda: PlaySound(VOICE_BUTTON, SND_ASYNC)

        w = MiniWin(self.root, '棋局库', 300, 393)
        toplevel, canvas = w.toplevel, w.canvas
        info = tkt.CanvasLabel(canvas, 5*S, 5*S, 200*S,
                               20*S, 5*S, font=('楷体', 10), justify='left')
        back = tkt.CanvasButton(
            canvas, 210*S, 5*S, 80*S, 20*S, 5*S, '←后退', font=('楷体', round(12*S)),
            command=lambda: canvas_set(path_.rsplit('/', 1)[0]))
        back.command_ex['press'] = lambda: PlaySound(VOICE_BUTTON, SND_ASYNC)
        content = tkt.Canvas(toplevel, int(290*S), int(357*S))
        content.configure(highlightthickness=1, highlightbackground='grey')
        content.bind('<MouseWheel>', scroll)
        content.place(x=5*S, y=30*S)
        path_ = './data'
        canvas_set(path_)

    @classmethod
    def chess(cls) -> None:
        """ 初始化棋子 """
        clear()
        for i in 1, 7:
            Chess('炮', i, 2, '#000000')
            Chess('砲', i, 7, '#FF0000')
        for x in range(0, 10, 2):
            Chess('兵', x, 6, '#FF0000')
            Chess('卒', x, 3, '#000000')
        for a, b, i in zip('车马象士将士象马车', '車馬相仕帥仕相馬車', range(9)):
            Chess(a, i, 0, '#000000')
            Chess(b, i, 9, '#FF0000')

    @classmethod
    def clock(cls, flag: list[int | None] = [0, None]) -> None:
        """ 计时 """
        if (flag[1] and flag[1] != Global.timer) or not Global.player:
            return statistic(Time=flag[0])
        if not flag[1]:
            Global.timer = flag[1] = time()
        cls.canvas.itemconfigure(
            cls.timer, text='%02d:%02d\n%s思考中.' % (*divmod(flag[0], 60), Global.player)+'.'*(flag[0] % 3))
        cls.root.after(1000, cls.clock, [flag[0]+1, flag[1]])

    @classmethod
    def touch(cls, event: Event) -> None:
        """ 高亮选棋 """
        flag = True
        for line in Global.chesses:
            for chess in line:
                if chess:
                    if chess.touch(event) and flag:
                        flag = False
                        cls.canvas.configure(cursor='hand2')
        if flag:
            cls.canvas.configure(cursor='arrow')

    @classmethod
    def choose(cls, event: Event, chess_=None) -> None:
        """ 选中棋子 """
        if not (Global.choose and cls.move(Global.choose, event)):
            for chess in [chess for line in Global.chesses for chess in line]:
                if chess and rule.ifop(chess, Global.player):
                    if chess.choose(event):
                        chess_ = chess
        Global.choose = chess_
        if chess_:
            chess_.move_pos = rule.rule(Global.chesses, chess_, True)
            if config['virtual']:
                for pos in chess_.move_pos:
                    chess_.virtual(*pos)

    @classmethod
    def move(cls, choose,  # type: Chess
             event: Event) -> bool | None:
        """ 移动棋子 """
        for flag, x_, y_ in choose.move_pos:
            x, y = (40+(choose.x+x_)*70)*S, (40+(choose.y+y_)*70)*S
            if hypot(event.x/tkt.S-x, event.y/tkt.S-y) < 30*S:
                if Global.mode == 'LAN':
                    LAN.API.send(
                        msg=(choose.x, choose.y, flag, x_, y_))
                choose.move(flag, x_, y_)
                choose.highlight(False, inside=False)
                choose = None
                if Global.mode in 'COMPUTER END':
                    cls.root.after(700, Thread(
                        target=lambda: Window.AImove('#000000'), daemon=True).start)
                rule.switch()
                return True

    @classmethod
    def AImove(cls, color: str, flag: bool = False) -> None:
        """ 电脑移动 """
        if not Global.player:
            return
        # statistic(AI=1)
        data, score = intelligence(Global.chesses, color, config['level'])
        print('\033[33mSCORE\033[0m:', score)
        pos, delta = data
        Global.chesses[pos[1]][pos[0]].move(*delta)
        rule.switch()
        if flag and Global.mode == 'TEST':
            color = '#FF0000' if color == '#000000' else '#000000'
            cls.root.after(600, Thread(target=cls.AImove,
                           args=(color, True), daemon=True).start)

    @classmethod
    def tip(cls, text: str, stay: int = 3000) -> None:
        """ 产生一个提示框 """
        label = tkt.CanvasLabel(
            cls.canvas, -250*S, 10*S, 240*S, 120*S, 20*S, text, font=('楷体', round(15*S)),
            color_outline=['black', 'black'])
        icon = tkt.CanvasLabel(
            cls.canvas, -240*S, 20*S, 30*S, 30*S, 15*S, ' i  ', font=('华文隶书', round(20*S), 'bold'),
            color_text=['#4884B4', '#4884B4'], color_outline=['grey', 'grey'], color_fill=tkt.COLOR_NONE)
        tkt.move(cls.canvas, label, 260*S, 0, 500, 'smooth')
        tkt.move(cls.canvas, icon, 260*S, 0, 500, 'smooth')
        cls.root.after(
            stay, tkt.move, cls.canvas, label, -260*S, 0, 500, 'smooth')
        cls.root.after(
            stay, tkt.move, cls.canvas, icon, -260*S, 0, 500, 'smooth')
        cls.root.after(stay+1000, label.destroy)
        cls.root.after(stay+1000, icon.destroy)

    @classmethod
    def test(cls, color: str = '#FF0000') -> None:
        """ 测试模式 """
        rule.modechange('TEST')
        cls.root.after(4000, Thread(
            target=cls.AImove, args=(color, True), daemon=True).start)


class MiniWin:
    """ 小窗口 """

    def __init__(self, root: tkt.Tk, title: str, width: int, height: int) -> None:
        self.toplevel = tkt.Toplevel(
            root, title, int(width*S), int(height*S),
            (SCREEN_WIDTH - tkt.S * width * S)//2,
            (SCREEN_HEIGHT - tkt.S * height * S)//2)
        self.toplevel.resizable(False, False)
        self.toplevel.transient(root)
        self.canvas = tkt.Canvas(self.toplevel, width*S, height*S)
        self.canvas.place(x=0, y=0)


class Chess:
    """ 棋子 """

    def __init__(self, name: str, x: int, y: int, color: bool) -> None:
        """ 初始化 """
        self.name = name  # 名称，区分类别
        self.color = color  # 颜色，区分红黑
        self.x, self.y = x, y
        Global.chesses[y][x] = self
        x, y = 40+x*70, 40+y*70
        self.items = [
            Window.canvas.create_oval(  # 阴影
                (x-28)*S, (y-28)*S, (x+32)*S, (y+32)*S, fill='#505050', width=0),
            Window.canvas.create_oval(  # 外框
                (x-30)*S, (y-30)*S, (x+30)*S, (y+30)*S, fill='#B49632'),
            Window.canvas.create_oval(  # 内框
                (x-27)*S, (y-27)*S, (x+27)*S, (y+27)*S, fill='#D2B450', width=0),
            Window.canvas.create_text(  # 文字
                x*S, y*S, text=name, font=('楷体', round(27*S), 'bold'), fill=color)
        ]  # type: list[int]
        self.virtual_items = []  # type: list[int]
        self.attack_chess = []  # type: list[Chess]
        self.move_pos: list[tuple[int, int]] = []

    def lift(self) -> None:
        """ 提升位置 """
        Window.canvas.lift(self.items[0])
        Window.canvas.lift(self.items[1])
        Window.canvas.lift(self.items[2])
        Window.canvas.lift(self.items[3])

    def move(self, flag: bool, x: int, y: int, cache: bool = False) -> None:
        """ 移动 """
        # statistic(Move=1)
        self.lift()
        self.virtual_delete()
        self.x += x
        self.y += y

        if not cache:
            Global.chesses[self.y-y][self.x-x] = None
            Global.index += 1
            if Global.index == len(Global.cache):  # 新增
                Global.cache.append(  # (目标者名称，目标位置，回退位移)
                    (getattr(Global.chesses[self.y][self.x], 'name', None), (self.x, self.y), (-x, -y)))
            else:  # 覆盖
                Global.cache[Global.index] = (
                    (getattr(Global.chesses[self.y][self.x], 'name', None), (self.x, self.y), (-x, -y)))

        def update() -> None:
            """ 更新并播放音效 """
            if flag:
                statistic(Eat=1)
                Global.count = 0
                Global.chesses[self.y][self.x].destroy()
            else:
                Global.count += 1
            Global.chesses[self.y][self.x] = self
            if rule.peace():  # 和棋
                rule.gameover()
                if Global.mode == 'LAN':
                    LAN.API.close()
            elif not (color := rule.warn(Global.chesses, self.color)):
                file = VOICE_EAT if flag else VOICE_DROP
                PlaySound(file, SND_ASYNC)
            else:
                PlaySound(VOICE_WARN, SND_ASYNC)
                statistic(Warn=1)
                if rule.dead(Global.chesses, color[0]):  # 绝杀
                    rule.gameover(color[0])
                    if Global.mode == 'LAN':
                        LAN.API.close()

            print_chess(Global.chesses)

        for item in self.items:
            tkt.move(Window.canvas, item, x*70*S, y*70*S, 500, 'smooth',
                     end=update if not self.items.index(item) else None)

    def destroy(self) -> None:
        """ 摧毁棋子 """
        Window.canvas.delete(*self.items)
        self.virtual_delete()

    def highlight(self, condition: bool, color: str | None = None, inside: bool = True) -> bool:
        """ 棋子高亮 """
        if condition:
            if not inside:
                PlaySound(VOICE_CHOOSE, SND_ASYNC)
            Window.canvas.itemconfigure(self.items[1+inside], fill=color)
        else:
            color_ = '#D2B450' if inside else '#B49632'
            Window.canvas.itemconfigure(self.items[1+inside], fill=color_)
        return condition

    def touch(self, event: Event) -> bool:
        """ 触碰棋子 """
        x, y = (40+self.x*70)*S, (40+self.y*70)*S
        condition = hypot(event.x/tkt.S-x, event.y/tkt.S-y) < 30*S
        return self.highlight(condition, '#E4D296')

    def choose(self, event: Event) -> bool:
        """ 选中棋子 """
        x, y = (40+self.x*70)*S, (40+self.y*70)*S
        condition = hypot(event.x/tkt.S-x, event.y/tkt.S-y) < 30*S
        if not self.highlight(condition, '#00FF00', False):
            self.virtual_delete()
        return condition

    def virtual(self, flag: bool, x: int, y: int) -> None:
        """ 虚位显示 """
        if flag:
            chess = Global.chesses[self.y+y][self.x+x]
            self.attack_chess.append(chess)
            chess.highlight(True, '#FF0000', False)
        else:
            x, y = 40+(self.x+x)*70, 40+(self.y+y)*70
            self.virtual_items.append(Window.canvas.create_oval(  # 外框
                (x-30)*S, (y-30)*S, (x+30)*S, (y+30)*S, fill='', outline=VIRTUAL_OUTLINE))
            self.virtual_items.append(Window.canvas.create_oval(  # 内框
                (x-27)*S, (y-27)*S, (x+27)*S, (y+27)*S, fill='', outline=VIRTUAL_INSIDE))
            self.virtual_items.append(Window.canvas.create_text(  # 文字
                x*S, y*S, text=self.name, font=('楷体', int(27*S), 'bold'),
                fill=VIRTUAL_RED if self.color == '#FF0000' else VIRTUAL_BLACK))

    def virtual_delete(self) -> None:
        """ 删除虚位显示 """
        for chess in self.attack_chess:
            chess.highlight(False, inside=False)
        self.attack_chess.clear()
        Window.canvas.delete(*self.virtual_items)


def about() -> None:
    """ 关于页面 """
    info = '版本: %s\n日期: %s\t\t\n作者: %s' % (
        __version__, __update__, __author__)
    messagebox.showinfo('关于', message=info)


def logo(canvas: tkt.Canvas) -> None:
    """ 给画布加上标志背景 """
    x, y, color = canvas.width[1]//2 + 10*S, canvas.height[1]//2, '#DDD'
    canvas.create_text(
        x-100*S, y-20*S, text='中', fill=color, font=('华文行楷', round(115*S)))
    canvas.create_text(
        x-35*S, y+35*S, text='国', fill=color, font=('华文行楷', round(100*S)))
    canvas.create_text(
        x+35*S, y-35*S, text='象', fill=color, font=('华文行楷', round(75*S)))
    canvas.create_text(
        x+80*S, y+45*S, text='棋', fill=color, font=('华文行楷', round(85*S)))


def more_set(toplevel: tkt.Toplevel, canvas: tkt.Canvas | None = None) -> None:
    """ 更多设置 """
    if not canvas:
        canvas = tkt.Canvas(toplevel, 300*S, 150*S, expand=False)
        canvas.place(x=0, y=0)
        tkt.CanvasButton(
            canvas, 214*S, 121*S, 80*S, 23*S, 6*S, '返回', font=('楷体', round(12*S)), command=canvas.destroy
        ).command_ex['press'] = lambda: PlaySound(VOICE_BUTTON, SND_ASYNC)

    ttk.Style(canvas).configure('TCheckbutton', font=('楷体', round(12*S)))
    canvas.create_text(75*S, 15*S, text='我方让子', font=('楷体', round(12*S)))
    canvas.create_text(225*S, 15*S, text='对方让子', font=('楷体', round(12*S)))
    ttk.Checkbutton(canvas, text='我方先手', variable=toplevel.var_list[0], onvalue=1, offvalue=0).place(
        width=100*tkt.S*S, height=30*tkt.S*S, x=10*tkt.S*S, y=117*tkt.S*S)

    for y_, y in enumerate([30, 60, 90]):
        for x_, x in enumerate([10, 85, 160, 235]):
            i = y_*4+x_
            text = ('右' if i & 1 else '左') + '車车砲炮馬马'[i//2]
            ttk.Checkbutton(canvas, text=text, onvalue=1, offvalue=0, variable=toplevel.var_list[i+1]).place(
                width=100*tkt.S*S, height=30*tkt.S*S, x=x*tkt.S*S, y=y*tkt.S*S)


def clear() -> None:
    """ 清空棋盘 """
    for y, line in enumerate(Global.chesses):
        for x, chess in enumerate(line):
            if chess:
                chess.destroy()
                Global.chesses[y][x] = None


def open_file(path: str | None = None) -> None:
    """ 打开文件 """
    if path or (path := filedialog.askopenfilename(title='导入棋局', filetypes=[('象棋文件', '*.fen')])):
        try:
            with open(path, 'r', encoding='utf-8') as file:
                code, first = file.read().split()
            fen = {value: key for key, value in FEN.items()}
            clear()
            for y, line in enumerate(code.split('/')):
                x = 0
                for i in line:
                    if i.isalpha():
                        color = '#FF0000' if i.isupper() else '#000000'
                        Chess(fen[i], x, y, color)
                    x += int(i) if i.isdigit() else 1
            Global.first = first != 'b'
            rule.modechange('END')
        except:
            Window.tip('— 提示 —\n象棋文件格式不正确！\n导入棋局失败！')


def save_file(code: str = '') -> None:
    """ 另存为文件 """
    if path := filedialog.asksaveasfilename(
            title='导出棋局', filetypes=[('象棋文件', '*.fen')], initialfile='Chess.fen'):
        for line in Global.chesses:
            code, count = code + '/', 0
            for chess in line:
                if chess:
                    code += str(count)+FEN[chess.name]
                    count = 0
                else:
                    count += 1
            code += str(count)
        first = 'r' if Global.first else 'b'
        with open(path, 'w', encoding='utf-8') as file:
            file.write('%s %s' % (code.replace('0', '')[1:], first))


def LANmove() -> None:
    """ 局域网移动 """
    while True:
        x, y, flag, x_, y_ = LAN.API.recv()['msg']
        if (x, y) == (x_, y_):
            return
        Global.chesses[9-y][8-x].move(flag, -x_, -y_)
        rule.switch()
