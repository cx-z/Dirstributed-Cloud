#-*-coding:utf-8-*-
"""
数据中心的类结构
"""


class DataCenter:
    def __init__(self,id:int,ip:str,port:int,mem:int,unitMemPrice:int,unitCpuPrice:int) -> None:
        super().__init__()
        self.id:int = id
        self.addr = (ip,port)
        self.totalmem:int = mem
        self.leftmem:int = mem
        self.leftcpu:float = 1
        self.unitMemprice:int = unitMemPrice
        self.unitCpuPrice:int = unitCpuPrice
        self.current_income = 0
        self.neighbors = list() # 此节点的邻接节点
        self.weight = 0
        