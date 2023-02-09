"""
所有常量
"""

from socket import gethostbyname, gethostname
from tkinter import Tk

import tkintertools as tkt
from configure import config, configure

# 当前地址
ADDRESS = gethostbyname(gethostname())
# 默认端口
PORT = 10086
# 服务器地址
SERVER = '192.168.0.106'

# 红方虚拟棋子文本颜色
VIRTUAL_RED = '#D05C2D'
# 黑方虚拟棋子文本颜色
VIRTUAL_BLACK = '#845C2D'
# 虚拟棋子外框颜色
VIRTUAL_OUTLINE = '#845C2D'
# 虚拟棋子外框颜色
VIRTUAL_INSIDE = '#A06F36'
# 棋盘背景颜色
BACKGROUND = '#BC8340'

# 棋子分值
EXIST_DICT = {
    '将': 1000,
    '士': 4,
    '象': 4,
    '马': 8,
    '车': 18,
    '炮': 9,
    '卒': 3,
    '帥': 1000,
    '仕': 4,
    '相': 4,
    '馬': 8,
    '車': 18,
    '砲': 9,
    '兵': 3
}

# FEN棋谱规定
FEN = {
    '将': 'k',
    '士': 'a',
    '象': 'b',
    '马': 'n',
    '车': 'r',
    '炮': 'c',
    '卒': 'p',
    '帥': 'K',
    '仕': 'A',
    '相': 'B',
    '馬': 'N',
    '車': 'R',
    '砲': 'C',
    '兵': 'P'
}

# 统计数据名称对照表
STATISTIC_DICT = {
    "Launch": '程序启动次数',
    "LAN": '联机模式使用次数',
    "LOCAL": '双人模式使用次数',
    "COMPUTER": '人机模式使用次数',
    "END": '残局模式使用次数',
    "TEST": '测试模式使用次数',
    "Revoke": '悔棋次数',
    "Recovery": '撤销悔棋次数',
    "AI": 'AI功能调用次数',
    "Eat": '吃棋次数',
    "Move": '移棋次数',
    "Warn": '“将军”次数',
    "Win": '游戏胜利次数',
    "Lose": '游戏失败次数',
    "Peace": '和棋次数',
    "Play": '对局次数',
    "Time": '总游戏时间',
    "First": '先手次数'
}

# 选子音效
VOICE_CHOOSE = 'audio/choose.wav'
# 落子音效
VOICE_DROP = 'audio/drop.wav'
# 吃子音效
VOICE_EAT = 'audio/eat.wav'
# “将军”音效
VOICE_WARN = 'audio/warn.wav'
# 按钮音效
VOICE_BUTTON = 'audio/button.wav'

_TK = Tk()
_TK.withdraw()

# 屏幕宽度
SCREEN_WIDTH = _TK.winfo_screenwidth()
# 屏幕高度
SCREEN_HEIGHT = _TK.winfo_screenheight()

# 窗口缩放系数
if config['auto_scale']:
    S = float('%.3f' % (SCREEN_HEIGHT/tkt.S/(710+34*tkt.S)))
    configure(scale=S)
else:
    S = config['scale']

# 棋子移动分
# MOVE_DICT = {
#     '卒': 0,
#     '将': 1,
#     '士': 2,
#     '象': 3,
#     '马': 4,
#     '炮': 5,
#     '车': 6,
#     '兵': 0,
#     '帥': 1,
#     '仕': 2,
#     '相': 3,
#     '馬': 4,
#     '砲': 5,
#     '車': 6
# }

# 棋子位置分
# POS_LIST = [
#     [100, 120, 80,  250, 500,  250, 80,  120, 100],
#     [20,  80,  400, 200, 1000, 200, 400, 80,  20],
#     [60,  80,  100, 160, 200,  160, 100, 80,  60],
#     [40,  80,  60,  80,  160,  80,  60,  80,  40],
#     [20,  60,  20,  100, 60,   100, 20,  60,  20],
#     [20,  60,  20,  100, 60,   100, 20,  60,  20],
#     [40,  80,  60,  80,  160,  80,  60,  80,  40],
#     [60,  80,  100, 160, 200,  160, 100, 80,  60],
#     [20,  80,  400, 200, 1000, 200, 400, 80,  20],
#     [100, 120, 80,  250, 500,  250, 80,  120, 100]]
