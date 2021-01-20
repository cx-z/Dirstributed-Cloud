#-*-coding:utf-8-*-

import sys

from DataCenter import DataCenter
from Edge import Edge
from Manager import Manager


class Path:
    def __init__(self, path:tuple, delay:int) -> None:
        super().__init__()
        self.nodes = list()
        self.edges = list()
        self.band_cost = 0
        self.greedy_cost = 0
        self.propagation_delay = delay
        self.process_delay:int = sys.maxsize
        self.process_source:float = 0
        self.weight:float = 0 # 路径选择权重
        self.profit = 0 # 选定路径和节点后，最终的利润
        self.init_edges(path)
        self.init_nodes(path)
        
    def init_nodes(self, path:tuple):
        for v in path:
            node = DataCenter(v,"",40001,0,0,0)
            Manager().load_node_info(node)
            self.nodes.append(node)

    def init_edges(self, path:tuple):
        edges = list()
        for i in range(len(path)-1):
            e = Edge(path[i],path[i+1],0,0)
            Manager().load_edge_info(e)
            edges.append(e)
