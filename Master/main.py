#-*-coding:utf-8-*-
from Shop import Shop
from Sender import Sender
import threading


class Master:
    def __init__(self) -> None:
        super().__init__()
        self.shop = Shop()
        #self.sender = Sender("172.16.111.1",40000)
        t1 = threading.Thread(target=self.shop.sale)
        t2 = threading.Thread(target=self.shop.monitor)
        t1.start()
        t2.start()
       

if __name__ == "__main__":
    # msg = "192.168.1.2\n"
    # msg += "192.168.1.3\n"
    # msg += "vnf1,baifenmao/get-started:template1,1.5,4m\n"
    # msg += "vnf2,baifenmao/get-started:template1,1.5,4m\n"
    master = Master()