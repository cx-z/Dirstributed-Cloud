# -*-coding:utf-8-*-
import socket
import threading
import config


class Receiver:
    def __init__(self):
        super().__init__()
        self.addr = (config.LOCAL_IP,config.LOCAL_PORT)
        self.bufSize = 2048
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(self.addr)
        self.socket.listen(10)
        self.msgs = set()

    # 接收从master发来的功能链信息
    def receive(self, lock:threading.Lock):
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
                        lock.acquire()
                        # print("Reciver已获取锁")
                        self.msgs.add(msg.decode())
                        lock.release()
                        # print("Reciver已释放锁")
                        flag = False
                        break
                except KeyboardInterrupt:
                    print("键入终止")
                    break
                except:
                    continue
        print("通信结束")
        self.socket.close()

