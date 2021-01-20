# -*-coding:utf-8 -*-
"""
拓扑图
"""
import heapq
import sys
import copy

import config
from DataCenter import DataCenter
from Singleton import Singleton
from Manager import Manager


class Graph(metaclass=Singleton):
    def __init__(self) -> None:
        super().__init__()
        self.graph = dict() # 元素结构为 node:{node:[weight,bandwidth],...}
        self.nodes = list()
        self.edges = set()
        self.make_graph()
    
    # 将数据库DataCenters中的节点信息储存在self.nodes中
    def load_nodes(self)->None:
        sql = """SELECT * FROM DataCenters"""
        nodes = Manager().exec_sql(sql)
        for i in range(len(nodes)):
            node = DataCenter(nodes[i][0],nodes[i][1],nodes[i][2],nodes[i][3],nodes[i][5], nodes[i][6])
            # DataCenter的neighbors属性保存邻接节点的id
            for item in self.graph[i]:
                if item != 0:
                    node.neighbors.append(item)
            self.nodes.append(node)

    def load_edge(self, ed1, ed2)->None:
        sql = """SELECT * FROM Edges WHERE end"""
        nodes = Manager().exec_sql(sql)

    def make_graph(self)->None:
        self.graph = config.GRAPH
        # for i in config.GRAPH:
        #     adjs = dict() # adjs已经指向新的内存，因此这里不需考虑深浅拷贝
        #     for j in config.GRAPH[i]:
        #         e = Edge(i,j,0,0)
        #         Manager().load_edge_info(e)
        #         self.edges.add(e)
        #         adjs[j] = [e.totalBandWidth, e.propagationDelay]
        #     self.graph[i] = adjs

    def checkCircle(self,path:tuple):
        nodes = set()
        for i in path:
            if i in nodes:
                return True
            else:
                nodes.add(i)
        return False

    def getMinDistancesIncrement(self, inputList:list):
        inputList.sort()
        lenList = [v[0] for v in inputList]
        minValue = min(lenList)
        minValue_index = lenList.index(minValue)
        # minPath应为一个数组
        # 因此inputList中的元素结构为 [距离，[路径]]
        minPath = copy.deepcopy([v[1] for v in inputList][minValue_index])
        return minValue, minPath, minValue_index

    def k_shortest_paths(self,start, finish, k = 3):
        '''
        :param start: 起始点
        :param finish: 终点
        :param k: 给出需要求的最短路数
        :return: 返回K最短路和最短路长度
        该算法重复计算了最短路，调用get_shortest_path()方法只是用到了起始点到其他所有点的最短距离和最短路长度
        '''
        distances, _, shortestPathLen = self.get_shortest_path(start, finish)
        num_shortest_path = 0
        paths = dict()
        distancesIncrementList = [[0, [finish]]]
        # k要注意，不能太大，否则永远都循环不完了
        # 后面有余力，再改进
        while len(paths) < k:
            path = []
            #distancesIncrementList = self.deleteCirclesWithEndpoint(distancesIncrementList,finish)
            minValue, minPath, minIndex = self.getMinDistancesIncrement(distancesIncrementList)
            min_vertex = minPath[-1]
            distancesIncrementList.pop(minIndex)
 
            if min_vertex == start:
                path.append(minPath[::-1])
                num_shortest_path += 1
                # type(path) -> list,不能作为字典的key
                # 由于list不可哈希，因此转换成元组
                if self.checkCircle(path[0]):
                    continue
                paths[tuple(path[0])] = minValue + shortestPathLen
                # 字典采用{path ; pathlen}这样的键值对，不能使用{pathlen:path}
                # 因为key是唯一的，所以在此相同长度的path只能保存一个，后来的会覆盖前面的
                # paths[minValue + shortestPathLen] = path
                continue
            for neighbor in self.graph[min_vertex]:
                incrementValue:list = minPath
                increment = 0
                if neighbor == finish:
                    # 和函数deleteCirclesWithEndpoint()作用一样
                    continue
                if distances[min_vertex] == (distances[neighbor] + self.graph[min_vertex][neighbor][0]):
                    increment = minValue
                elif distances[min_vertex] < (distances[neighbor] + self.graph[min_vertex][neighbor][0]):
                    increment = minValue + distances[neighbor] + self.graph[min_vertex][neighbor][0] - distances[min_vertex]
                elif distances[neighbor] == (distances[min_vertex] + self.graph[min_vertex][neighbor][0]):
                    increment = minValue + 2 * self.graph[min_vertex][neighbor][0]
                temp = copy.deepcopy(incrementValue)
                temp.append(neighbor)
                distancesIncrementList.append([increment, temp])
        return paths


    def get_shortest_path(self, start, end) -> int and list and int:
        # distances使用字典的方式保存每一个顶点到startpoint点的距离
        distances = {}
        # 从startpoint到某点的最优路径的前一个结点
        # eg:startpoint->B->D->E,则previous[E]=D,previous[D]=B,等等
        previous = {}
        # 用来保存图中所有顶点的到startpoint点的距离的优先队列
        # 这个距离不一定是最短距离
        nodes = []
        # Dikstra算法 数据初始化
        for vertex in self.graph:
            if vertex == start:
                # 将startpoint点的距离初始化为0
                distances[vertex] = 0
                heapq.heappush(nodes, [0, vertex])
            elif vertex in self.graph[start]:
                # 把与startpoint点相连的结点距离startpoint点的距离初始化为对应的弧长/路权
                distances[vertex] = self.graph[start][vertex][0]
                heapq.heappush(nodes, [self.graph[start][vertex][0], vertex])
                previous[vertex] = start
            else:
                # 把与startpoint点不直接连接的结点距离startpoint的距离初始化为sys.maxsize
                distances[vertex] = sys.maxsize
                heapq.heappush(nodes, [sys.maxsize, vertex])
                previous[vertex] = None

        shortest_path = []
        lenPath = sys.maxsize
        while nodes:
            # 取出队列中最小距离的结点
            smallest = heapq.heappop(nodes)[1]
            if smallest == end:
                shortest_path = []
                lenPath = distances[smallest]
                temp = smallest
                while temp != start:
                    shortest_path.append(temp)
                    temp = previous[temp]
                # 将startpoint点也加入到shortest_path中
                shortest_path.append(temp)
            if distances[smallest] == sys.maxsize:
                # 所有点不可达
                break
            # 遍历与smallest相连的结点，更新其与结点的距离、前继节点
            for neighbor in self.graph[smallest]:
                dis = distances[smallest] + self.graph[smallest][neighbor][0]
                if dis < distances[neighbor]:
                    distances[neighbor] = dis
                    # 更新与smallest相连的结点的前继节点
                    previous[neighbor] = smallest
                    for node in nodes:
                        if node[1] == neighbor:
                            # 更新与smallest相连的结点到startpoint的距离
                            node[0] = dis
                            break
                    heapq.heapify(nodes)
        return distances, shortest_path, lenPath

if __name__ == '__main__':
    g = Graph()
    
    start = 1
    end = 5
    k = 10
    distances, shortestPath, shortestPathLen = g.get_shortest_path(start, end)
    print('{}->{}的最短路径是：{}，最短路径为：{}'\
        .format(start, end, shortestPath, shortestPathLen))

    paths = g.k_shortest_paths(start, end, k)
    print('\n求得的 {}-->{} 的 {}-最短路 分别是：'.format(start, end, k))
    index = 1
    for path, length in paths.items():
        print('{}:{} 最短路长度：{}'.format(index, path, length))
        index += 1