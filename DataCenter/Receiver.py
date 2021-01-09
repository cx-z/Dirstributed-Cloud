# -*-coding:utf-8-*-
import socket

from Container import Container


class Receiver:
    def __init__(self, ip: str, port: int):
        super().__init__()
        self.addr = (ip, port)
        self.bufSize = 2048
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(self.addr)
        self.socket.listen(10)

    # 接收从master发来的功能链信息
    def receive(self, containers: list):
        # 后续要做成一个线程，需考虑互斥
        flag = True  # 这个标志用于测试功能是否正常，后期部署本函数是死循环
        while flag:
            masterSocket, masterAddr = self.socket.accept()
            print("Connected from {}".format(masterAddr))
            while True:
                try:
                    msg = masterSocket.recv(self.bufSize)
                    if msg:
                        print("Receive message from sender")
                        masterSocket.close()
                        # 接收器将生成的容器信息列表保存在传入的实参cons中
                        cons = self.makeContainersList(msg.decode())
                        for item in cons:
                            containers.append(item)
                        flag = False
                        break
                except KeyboardInterrupt:
                    print("键入终止")
                    break
                except:
                    continue
        print("通信结束")
        self.socket.close()

    def makeContainersList(self, msg: str) -> list:
        # 后续要做成一个线程，需考虑互斥
        containers = list()
        for line in msg.splitlines():
            params = line.split(',')
            con = Container(params[0], params[1], params[2], params[3])
            containers.append(con)
        return containers


if __name__ == '__main__':
    dc = Receiver("172.16.111.1", 11001)
    containers = list()
    dc.receive(containers)
    for con in containers:
        con.createContainers()

