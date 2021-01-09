#-*-coding:utf-8-*-
import socket

class Sender:
    def __init__(self) -> None:
        super().__init__()
        self.addr = ("172.16.111.1",11000)
        self.bufSize = 2048
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(self.addr)

    # master只需将功能链的各个VNF以及每个容器的资源上限发送给目标数据中心        
    def sendsfc(self,dcAddr,sfc:str) -> None:
        self.socket.connect(dcAddr)
        print("Connected to the receiver")
        self.socket.send(sfc.encode())
        self.socket.close()

    def makeSFCMsg(self) -> str:
        msg = "docker run -it --name=vnf baifenmao/get-started:template1"
        return msg


server = Sender()
msg = "vnf1,baifenmao/get-started:template1,1.5,4m\n"
msg += "vnf2,baifenmao/get-started:template1,1.5,4m\n"
server.sendsfc(("172.16.111.1",11001),msg)
