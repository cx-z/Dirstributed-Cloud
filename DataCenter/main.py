# -*-coding:utf-8-*-
import socket
import fcntl
import struct
from Receiver import Receiver
from OpenvSwitch import OpenvSwitch


class DataCenter:
    def __init__(self) -> None:
        super().__init__()
        self.entry: str = "ens9"
        self.exit: str = "ens10"
        self.reciver: str = Receiver(self.getLocalIp(), 40001)
        self.sfcs: set = set()
        self.ovs: OpenvSwitch = OpenvSwitch()

    def getLocalIp(self):  # 获取IP地址
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # IPv4,UDP
        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', "ens3")  # ens3是服务器虚拟机上网的网卡名
        )[20:24])

  
if __name__ == "__main__":
    pass