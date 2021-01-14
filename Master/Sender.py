# -*-coding:utf-8-*-
import socket
from Request import Request
import config

class Sender:
    def __init__(self) -> None:
        super().__init__()
        self.addr = (config.LOCAL_IP, config.LOCAL_PORT)
        self.bufSize = 2048
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(self.addr)

    # master只需将功能链的各个VNF以及每个容器的资源上限发送给目标数据中心
    def sendsfc(self, dcAddr, sfc: str) -> None:
        self.socket.connect(dcAddr)
        print("Connected to the receiver")
        self.socket.send(sfc.encode())
        self.socket.close()

    def makeSFCMsg(self, req: Request) -> str:
        msg = str(req.id) + "\n"
        msg += req.src + "\n"
        msg += req.dst + "\n"
        for v in req.sfc:
            msg += "vnf3" +','+ v + ',' + "0.25" + ',' + "400m" + "\n"
        return msg
