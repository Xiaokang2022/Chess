"""
客户端功能
"""

from socket import socket

from constants import PORT, SERVER


class Client:
    """ 客户端 """

    def __init__(self) -> None:
        self.client = socket()
        self.login = False
        self.client.settimeout(3)

    def connect(self) -> bool:
        """ 连接服务端 """
        out = self.client.connect_ex((SERVER, PORT))
        return out == 0

    def verify(self) -> bool | None:
        """ 身份验证 """
        try:
            self.send(type='CLIENT')
            back = self.recv()['type']
            if back == 'SERVER':
                return True
            else:
                self.close()
        except:
            return False

    def close(self) -> None:
        """ 断开连接 """
        self.send(op='Quit')
        self.client.close()
        print(123)

    def send(self, **kw) -> bool:
        """ 发送信息 """
        try:
            self.client.send(kw.__repr__().encode('utf-8'))
            return True
        except:
            return False

    def recv(self) -> dict:
        """ 接收信息 """
        try:
            data = self.client.recv(4096)
            return eval(data)
        except:
            return {}

    def run(self) -> None:
        """ 开始运行 """
        if self.connect():
            print('CONNECT SUCCESS')
        else:
            print('ERROR IN CONNECT')
        if self.verify():
            print('VERIFY SUCCESS')
        else:
            print('ERROR IN VERIFY')
        self.send(op='Mail', mail='392126563@qq.com')
        self.send(code=input('code:'), psd='2023', nick='Admin')
        rtn = self.recv()
        if rtn.get('act', None):
            print(rtn['act'])
        else:
            print(rtn['info'])
        self.close()


client = Client()
client.run()
