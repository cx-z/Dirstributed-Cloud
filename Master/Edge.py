#-*-coding:utf-8-*-
"""
边的类结构
"""


class Edge:
    def __init__(self, endpoint1, endpoint2, bandwidth, unitprice) -> None:
        super().__init__()
        self.endpoint1 = endpoint1
        self.endpoint2 = endpoint2
        self.totalBandWidth = bandwidth
        self.leftBandWidth = bandwidth
        self.unitprice = unitprice
        self.current_income = 0 # 指当前运行的服务的总收费
