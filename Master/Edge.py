#-*-coding:utf-8-*-
"""
边的类结构
"""


class Edge:
    def __init__(self, endpoint1, endpoint2, bandwidth, unitprice) -> None:
        super().__init__()
        self.endpoint1:int = endpoint1
        self.endpoint2:int = endpoint2
        self.propagationDelay:int = 0
        self.totalBandWidth:int = bandwidth
        self.leftBandWidth:int = bandwidth
        self.unitprice:int = unitprice
        self.current_income:int = 0 # 指当前运行的服务的总收费
