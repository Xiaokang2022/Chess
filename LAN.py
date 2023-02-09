"""
局域网功能
"""

from socket import SOCK_DGRAM, socket
from threading import Thread
from tkinter import messagebox, ttk
from winsound import SND_ASYNC, PlaySound

import GUI
import tkintertools as tkt
from constants import ADDRESS, PORT, VOICE_BUTTON, S
from rule import modechange


class _Base:
    """ 基本功能 """

    def __init__(self, toplevel: tkt.Toplevel) -> None:
        self.socket = socket()  # 套接字
        self.connection: socket | None = None  # 连接对象
        self.baseUI(toplevel)
        self.flag = False

    def baseUI(self, toplevel: tkt.Toplevel) -> None:
        """ 基本UI界面 """
        self.toplevel = toplevel
        self.canvas = tkt.Canvas(
            self.toplevel, 300*S, 150*S, bg='#FFFFFF', expand=False)
        self.canvas.place(x=0, y=0)
        self.canvas.create_rectangle(
            -1, 115*S, 301*S, 151*S, width=0, fill='#F1F1F1')

        self.again = tkt.CanvasButton(
            self.canvas, 42*S, 121*S, 80*S, 23*S, 6*S, font=('楷体', round(12*S)))
        self.again.command_ex['press'] = lambda: PlaySound(
            VOICE_BUTTON, SND_ASYNC)
        self.ok = tkt.CanvasButton(
            self.canvas, 128*S, 121*S, 80*S, 23*S, 6*S, font=('楷体', round(12*S)))
        self.ok.command_ex['press'] = lambda: PlaySound(
            VOICE_BUTTON, SND_ASYNC)
        self.cancel = tkt.CanvasButton(
            self.canvas, 214*S, 121*S, 80*S, 23*S, 6*S, font=('楷体', round(12*S)), text='取消', command=self.close)
        self.cancel.command_ex['press'] = lambda: PlaySound(
            VOICE_BUTTON, SND_ASYNC)
        self.again.set_live(False)

    def send(self, **kw) -> int:
        """ 发送消息 """
        try:
            if self.connection:
                return self.connection.send(kw.__repr__().encode('utf-8'))
            return self.socket.send(kw.__repr__().encode('utf-8'))
        except ConnectionResetError:
            pass

    def recv(self, __bufsize: int = 1024) -> dict:
        """ 接收消息 """
        try:
            if self.connection:
                return eval(self.connection.recv(__bufsize).decode('utf-8'))
            return eval(self.socket.recv(__bufsize).decode('utf-8'))
        except ConnectionResetError:
            pass

    def close(self) -> None:
        """ 关闭联机功能 """
        self.flag = True
        self.socket.close()
        self.canvas.destroy()


class Server(_Base):
    """ 服务端 """

    def __init__(self, toplevel: tkt.Toplevel) -> None:
        _Base.__init__(self, toplevel)
        self.UI()
        Thread(target=self.accept, daemon=True).start()
        self.timer()

    def UI(self) -> None:
        """ 详细的UI界面 """
        self.again.configure(text='重新等待')
        self.again.command = lambda: (self.timer(), self.again.set_live(False))
        self.ok.configure(text='确定')
        self.ok.command = self.identify
        self.ok.set_live(False)
        self.text = self.canvas.create_text(
            150*S, 15*S, font=('楷体', round(12*S)))
        self.time_ = self.canvas.create_text(
            150*S, 65*S, font=('楷体', round(30*S)))

    def timer(self, ind: int = 60) -> None:
        """ 计时器 """
        self.canvas.itemconfigure(self.time_, text=str(ind))
        self.canvas.itemconfigure(self.text, text='正在等待其他电脑连接.'+-ind % 3*'.')
        if ind and not self.flag:
            self.toplevel.after(1000, self.timer, ind-1)
        elif not ind:
            self.socket.close()
            self.again.set_live(True)
            self.canvas.itemconfigure(self.text, text='没有电脑连接此电脑')
        else:
            self.flag = True
            self.canvas.itemconfigure(
                self.text, text='已连接: %s' % self.client_address[0])
            self.ok.set_live(True)

    def check(self) -> None:
        """ 检测 """
        server = socket(type=SOCK_DGRAM)  # UDP
        server.settimeout(1)
        server.bind(('', PORT-1))
        while not self.flag:
            try:
                _, address = server.recvfrom(4096)
                server.sendto(b'SERVER', address)
            except TimeoutError:
                pass
        else:
            server.close()

    def accept(self) -> None:
        self.socket.bind((ADDRESS, PORT))
        self.socket.listen(1)
        Thread(target=self.check, daemon=True).start()
        self.connection, self.client_address, self.flag = *self.socket.accept(), True

    def identify(self) -> None:
        """ 身份确认 """
        self.send(msg='OK')
        code = self.recv()['msg']
        modechange('LAN', code)
        self.toplevel.destroy()
        Thread(target=GUI.LANmove, daemon=True).start()


class Client(_Base):
    """ 客户端 """

    def __init__(self, toplevel: tkt.Toplevel) -> None:
        _Base.__init__(self, toplevel)
        self.UI()
        Thread(target=self.search, daemon=True).start()

    def UI(self) -> None:
        """ 详细的UI界面 """
        self.again.configure(text='重新搜索')
        self.again.command = lambda: (Thread(
            target=self.search, daemon=True).start(), self.again.set_live(False))
        self.ok.configure(text='连接')
        self.ok.command = self.connect
        self.canvas.create_text(
            10*S, 10*S, text='搜索进度', anchor='w', font=('楷体', round(10*S)))
        self.text = self.canvas.create_text(
            10*S, 60*S, text='可用连接(0)', anchor='w', font=('楷体', round(10*S)))
        self.bar = tkt.ProcessBar(
            self.canvas, 10*S, 25*S, 280*S, 15*S, font=('楷体', round(10*S)))
        self.combobox = ttk.Combobox(self.canvas)
        self.combobox.place(
            width=190*tkt.S*S, height=20*tkt.S*S, x=10*tkt.S*S, y=80*tkt.S*S)
        tkt.CanvasButton(
            self.canvas, 210*S, 80*S, 80*S, 20*S, 5*S, '更多', font=('楷体', round(10*S)),
            command=lambda: GUI.more_set(self.toplevel)
        ).command_ex['press'] = lambda: PlaySound(VOICE_BUTTON, SND_ASYNC)

    def search(self) -> None:
        """ 搜索 """
        def modify() -> None:
            """ 修改 """
            self.combobox['value'] = address_list
            self.canvas.itemconfigure(
                self.text, text='可用连接(%d)' % len(address_list))
        address_list = []
        modify()
        prefix = ADDRESS.rsplit('.', 1)[0]
        client = socket(type=SOCK_DGRAM)  # UDP
        client.settimeout(1e-4)
        for i in range(1, 255):
            address = '%s.%d' % (prefix, i)
            try:
                client.sendto(b'CLIENT', (address, PORT-1))
                data = client.recvfrom(4096)
                if data[0] == b'SERVER':
                    address_list.append(address)
                    modify()
            except (TimeoutError, ConnectionResetError):
                pass
            if self.flag:
                return client.close()
            self.bar.load(i/254)
        self.again.set_live(True)

    def connect(self) -> None:
        """ 连接 """
        address = self.combobox.get()
        if not address:
            return messagebox.showwarning('中国象棋', '请选择可用的目标地址！')
        try:
            self.socket.connect((address, PORT))
            messagebox.showinfo('中国象棋', '连接成功！\n请耐心等待对方点击确定')
            self.again.set_live(False)
            self.ok.set_live(False)
            Thread(target=self.identify, daemon=True).start()
        except:
            messagebox.showerror('中国象棋', '目标地址无效！')

    def identify(self) -> None:
        """ 身份确认 """
        if self.recv()['msg'] == 'OK':
            code = [str(v.get()) for v in self.toplevel.var_list]
            modechange('LAN', ''.join(code))
            for i in 1, 5, 9:
                code[i], code[i+3] = code[i+3], code[i]
                code[i+1], code[i+2] = code[i+2], code[i+1]
            code[0] = '0' if code[0] == '1' else '1'
            self.send(msg=''.join(code))
            self.toplevel.destroy()
            Thread(target=GUI.LANmove, daemon=True).start()


class API:
    """ 接口 """

    instance: Server | Client | None = None

    @classmethod
    def __init__(cls, toplevel: tkt.Toplevel, type_: str) -> None:
        if type_ == 'SERVER':
            cls.instance = Server(toplevel)
        else:
            cls.instance = Client(toplevel)

    @classmethod
    def send(cls, **kw) -> int:
        """ 发送信息 """
        return cls.instance.send(**kw)

    @classmethod
    def recv(cls, __bufsize: int = 1024) -> dict:
        """ 接收消息 """
        return cls.instance.recv(__bufsize)

    @classmethod
    def close(cls) -> None:
        """ 关闭套接字 """
        cls.instance.close()
