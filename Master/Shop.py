#-*-coding:utf-8-*-
import threading
import time
import heapq

import config
from Request import Request
from Caculator import Caculator
from Sender import Sender
from DataCenter import DataCenter
from Manager import Manager
from VNF import VNF


class Shop:
    def __init__(self) -> None:
        super().__init__()
        self.profit = 0
        self.caculator = Caculator([1,2])
        self.requests:list = [] # 按照offtime比较的自排序的堆
        self.lock = threading.Lock()

    # 一个死循环的线程，负责接受用户的请求、计算是否接受请求以及请求的部署方案，并进行回复
    def sale(self)->None:
        while True:
            req = self.input_request()
            profit,node = self.caculate_profit(req)
            if profit > 0:
                self.lock.acquire()
                req.offtime = time.time() + req.duration
                heapq.heappush(self.requests, req)
                self.lock.release()
                self.reply_customers()
                msg = Sender().makeSFCMsg(req)
                Sender().sendsfc(node.addr,msg)
                print(msg)
            if not config.FLAG:
                break

    # 用户输入请求
    def input_request(self)->Request:
        req = Request()
        req.id = len(self.requests)+1
        print("Please input your flow's source")
        req.src = input()
        print("Please input your flow's destination")
        req.dst = input()
        print("Please input your sfc, format is vnf1 vnf2 ...")
        sfc_vnf_name = input().split(" ")
        # print("Please input your bandwidth, the unit is M")
        # req.bid = int(input())
        # print("Please input your bid, the unit is doller")
        # req.bid = float(input())
        # print("Please input your maxDelay, the unit is ms")
        # req.maxDelay = int(input())
        print("Please input enter duration, the unit is seconds")
        req.duration = int(input())
        for i in range(len(sfc_vnf_name)):
            vnf = VNF(req.id,0,i+1,0,0,0)
            req.sfc.append(vnf)
        return req

    # 回复用户请求是否被接受
    def reply_customers(self)->None:
        print("sorry, your bid is not enough, you can improve your bid or give up")

    # 调用类Caculator的calculate_profit函数计算利润和应部署的节点
    # 此函数计算完利润后，需要修改req的属性，包括req.sfc里各个VNF的属性
    def caculate_profit(self,req:Request)->float and DataCenter:
        profit,node = Caculator().calculate_profit(req)
        return profit,node
        #return 100,DataCenter(1,"192.168.122.196",40001,400,1.5,100,100)

    def save_req_info(self, req:Request):
        Manager().insert_request_info(req)
        for v in req.sfc:
            Manager().insert_vnf_info(v)

    # 每隔一秒检查是否有服务要下线
    # 由于我们将请求保存在堆中，因此下限时间最近的请求在self.requests[0]
    def monitor(self):
        while True:
            self.lock.acquire()
            if self.requests[0].offtime >= time.time():
                Manager().del_request_info(self.requests[0])
                for v in self.requests[0].sfc:
                    Manager().del_vnf_info(v)
                heapq.heappop()
            self.lock.release()
            time.sleep(1)
            if not config.FLAG:
                break
