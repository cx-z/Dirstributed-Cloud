# -*-coding:utf-8 -*-
"""
本文件负责计算请求的部署节点以及利润
"""
from enum import Flag
import config

from Manager import Manager
from DataCenter import DataCenter
from Request import Request
from Edge import Edge
from Graph import Graph
from Path import Path


def cmp(x, y):
    if x<y:
        return -1
    elif x==y:
        return 0
    else:
        return 1

class Caculator:
    def __init__(self,nodes:list) -> None:
        super().__init__()
        
    # 计算请求的利润和部署的节点
    # 如果利润不为正，部署节点为0
    def calculate_profit(self,req:Request)->float and int:
        path:Path = self.choose_path()
        node:DataCenter = self.choose_node(req, path)
        return path.profit,node

    # 返回目标路径
    def choose_path(self,req:Request)->Path:
        k_paths:dict = Graph().k_shortest_paths(req.src, req.dst)
        paths = list()
        for p in k_paths:
            path:Path = Path(p, k_paths[p])
            if self.check_constraints(req, path):
                paths.append(path)
        if len(paths) == 0:
            return []
        for p in paths:
            self.path_weight(req, p)
        target_path:Path = paths[0]
        for p in paths:
            p:Path
            if p.weight > target_path.weight:
                target_path = p
        return target_path
        
    # 计算每条可用路径的选择权重
    def path_weight(self, req:Request, path:Path)->None:
        # path的最后两项是带宽成本和贪心利润
        min_band_edge:Edge = path.edges[0]
        for e in path.edges:
            e:Edge
            if e.leftBandWidth < min_band_edge.leftBandWidth:
                min_band_edge = e
        path.weight += path[-1] # 贪心利润
        path.weight += (req.bid/len(path.edges)\
            *(min_band_edge.totalBandWidth-min_band_edge.leftBandWidth)\
            /min_band_edge.current_income/req.bandwidth-1)\
            *min_band_edge.leftBandWidth

    # 从目标路径中选择部署节点
    # 此处输入的path最后三项依次是band_cost、greedy_profit和路径权重
    def choose_node(self,req:Request, path:Path)->DataCenter:
        # 首先计算部署在每个节点上的利润
        target_node:DataCenter = path.nodes[0].id
        for node in path.nodes:
            node:DataCenter
            node.weight += req.bid-path.band_cost-node.unitCpuPrice*path.process_source
            node.weight += ((req.bid-path.band_cost)*(1-node.leftcpu)/node.current_income/path.process_source-1)\
                *node.leftcpu
            if node.weight > target_node.weight:
                target_node = node
        path.profit = req.bid - path.band_cost - target_node.unitCpuPrice*path.process_source
        target_node.leftcpu -= path.process_source
        target_node.current_income += req.bid - path.band_cost
        Manager().update_node_info(target_node)
        return target_node

    def check_constraints(self,req:Request, path:Path)->bool:
        # 检查时延
        if path.propagation_delay >= req.maxDelay:
            return False
        # 检查带宽和带宽费用
        for e in path.edges:
            if e.leftBandWidth < req.bandwidth:
                return False
            path.band_cost += e.unitprice*req.bandwidth
        if path.band_cost >= req.bid:
            return False
        # 处理时延
        path.process_delay = min(req.maxDelay - path.propagation_delay, len(req.sfc)*req.bandwidth)
        # 判断算力是否满足条件
        # 所需最低算力
        for vnf in req.sfc:
            path.process_source += config.VNF_DELAY[vnf]
        path.process_source *= 1/path.process_delay
        # 判断是否有足够算力和最低算力开销
        for node in path.nodes:
            node:DataCenter
            # 判断节点剩余算力是否足够部署sfc
            if node.leftcpu < path.process_source:
                continue
            # 判断在该节点部署SFC是否亏本
            profit = req.bid - path.band_cost - node.unitCpuPrice*path.process_source
            if profit <= 0:
                continue
            # 上述两个条件都满足，表示可以在该路径部署，计算或更新贪心利润
            path.greedy_cost = max(profit, path.greedy_cost)
        # 没有可部署的节点，返回False
        return path.greedy_cost > 0
