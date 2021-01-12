# -*-coding:utf-8-*-
import os
from Container import Container
from OpenvSwitch import OpenvSwitch
import config


class SFC:
    def __init__(self, id: str, src: str, dst: str, containers: list, offtime, password: str) -> None:
        super().__init__()
        self.id: str = id
        self.src: str = src
        self.dst: str = dst
        self.offtime = offtime  # 下线时间，后面写
        self.password: str = password  # 本机的sudo密码
        self.containers:list = containers  # 此功能链的VNF容器集合
        self.interfaces: list = list()  # 此功能链的VNF接口

    # def __del__(self) -> None:
    #     # 终止并删除此SFC的所有容器
    #     for con in self.containers:
    #         os.system("docker stop {}".format(con.name))
    #         os.system("docker rm {}".format(con.name))
    #     self.containers.clear()
    #     # 清除此SFC连接在ovs上的所有端口
    #     # 由于config.ENTRY和config.EXIT是数据中心自带的网卡，其他SFC也要使用，不能从ovs上删除
    #     self.interfaces.remove(config.ENTRY)
    #     self.interfaces.remove(config.EXIT)
    #     for item in self.interfaces:
    #         OpenvSwitch().delPort(item,self.password)
    #     self.interfaces.clear()

    def createVNFs(self):
        # 根据给定的容器名、资源上限创建容器
        for con in self.containers:
            con.createContainers()
            # 为VNF创建网卡eth1和eth2时，同时已经在容器内配置了流量从eth1到eth2的流表
            # 且容器内的ovs只有一条流表，这样也可以避免广播风暴
            con.addInterfaceToContainer(self.password)
        # 配置流表项将容器串联起来，构成功能链
        self.addFlows()

    # 通过配置流表项将VNF串起来
    def addFlows(self) -> None:
        # interfaces数组中存储着流量流经此SFC的依次通过的所有网卡名
        # 首先从数据中心的config.ENTRY进入
        self.interfaces.append(config.ENTRY)
        for con in self.containers:
            # 从每个容器的eth1进入VNF
            self.interfaces.append(con.eth1)
            # 从每个容器的eth2离开VNF
            self.interfaces.append(con.eth2)
        # 最后从数据中心的config.EXIT离开
        self.interfaces.append(config.EXIT)
        for i in range(0,len(self.interfaces)-1,2):
            OpenvSwitch().addFlow("ip,nw_src={},nw_dst={},priority=1,in_port={},actions=output:{}"
                                  .format(self.src, self.dst, self.interfaces[i], self.interfaces[i+1]),self.password)
