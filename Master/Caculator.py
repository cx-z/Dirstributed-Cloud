# -*-coding:utf-8 -*-
"""
本文件负责计算请求的部署节点以及利润
"""
from DataCenter import DataCenter
from Request import Request


class Caculator:
    def __init__(self,nodes:list) -> None:
        super().__init__()
        
    # 计算请求的利润和部署的节点
    # 如果利润不为正，部署节点为0
    def calculate_profit(self,req:Request)->float and int:
        profit:float = 0
        node:DataCenter = self.choose_node(req)
        return profit,node

    def choose_node(self,req:Request)->int:
        node:DataCenter = DataCenter(1,"192.168.122.196",40001,400,1.5,100,100)
        return node