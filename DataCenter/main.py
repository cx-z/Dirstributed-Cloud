# -*-coding:utf-8-*-
import config
import threading
from SFC import SFC
import socket
import fcntl
import struct
from Receiver import Receiver
from OpenvSwitch import OpenvSwitch
from Container import Container


def getLocalIp():  # 获取IP地址
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # IPv4,UDP
        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', config.LOCAL_INTERFACE.encode())  # config.LOCAL_INTERFACE是服务器虚拟机上网的网卡名
        )[20:24])


class DataCenter:
    def __init__(self) -> None:
        super().__init__()
        self.reciver: Receiver = Receiver()
        self.sfcs: set = set()
        self.ovs: OpenvSwitch = OpenvSwitch()
        self.lock = threading.Lock()
        t1 = threading.Thread(target=self.checkMsg)
        t2 = threading.Thread(target=self.reciver.receive,args=(self.lock,))
        t1.start()
        t2.start()

    def checkMsg(self):
        flag = True
        while flag:
            self.lock.acquire()
            if len(self.reciver.msgs) == 0:
                self.lock.release()
                continue
            for msg in self.reciver.msgs:
                self.sfcs.add(self.makeSFC(msg))
                #print(msg)
            self.lock.release()
            self.reciver.msgs.clear()
            flag = False

    def makeSFC(self, msg: str) -> SFC:
        cons = list()
        lines = msg.splitlines()
        for i in range(3,len(lines),1):
            params = lines[i].split(',')
            con = Container(params[0], params[1], params[2], params[3])
            cons.append(con)
        sfc = SFC(lines[0],lines[1],lines[2],cons,"",config.PASSWORD)
        sfc.createVNFs()
        return sfc

  
if __name__ == '__main__':
    dc = DataCenter()
