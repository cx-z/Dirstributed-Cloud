# -*-coding:utf-8-*-
import os
from posix import listdir
from .Container import Container
from .OpenvSwitch import OpenvSwitch


class SFC:
    def __init__(self, id: str, src: str, dst: str, containers: list, offtime, password: str) -> None:
        super().__init__()
        self.id: str = id
        self.src: str = src
        self.dst: str = dst
        self.offtime = offtime  # 下线时间，后面写
        self.password: str = password  # 本机的sudo密码
        self.containers:list = containers  # 此功能链的VNF容器集合
        self.interfaces: list = list  # 此功能链的VNF接口
        # 根据给定的容器名、资源上限创建容器
        for con in self.containers:
            os.system("docker run -itd --privileged=true --name={} {}"
                      .format(con.name, con.type))
            con.addInterfaceToContainer(self.password)
        # 配置流表项将容器串联起来，构成功能链
        self.addFlows()

    def __del__(self) -> None:
        # 终止并删除此SFC的所有容器
        for con in self.containers:
            os.system("docker stop {}".format(con.name))
            os.system("docker rm {}".format(con.name))
        self.containers.clear()
        # 清除此SFC连接在ovs上的所有端口
        # 由于ens9和ens10是数据中心自带的网卡，其他SFC也要使用，不能从ovs上删除
        self.interfaces.remove("ens9")
        self.interfaces.remove("ens10")
        for item in self.interfaces:
            OpenvSwitch().delPort(item,self.password)
        self.interfaces.clear()

    # 通过配置流表项将VNF串起来
    def addFlows(self) -> None:
        # interfaces数组中存储着流量流经此SFC的依次通过的所有网卡名
        # 首先从数据中心的ens9进入
        self.interfaces.append("ens9")
        for con in self.containers:
            # 为VNF创建网卡eth1和eth2时，同时已经在容器内配置了流量从eth1到eth2的流表
            # 且容器内的ovs只有一条流表，这样也可以避免广播风暴
            con.addInterfaceToContainer(self.password)
            # 从每个容器的eth1进入VNF
            self.interfaces.append(con.eth1)
            # 从每个容器的eth2离开VNF
            self.interfaces.append(con.eth2)
        # 最后从数据中心的ens10离开
        self.interfaces.append("ens10")
        for i in range(len(self.interfaces)-1):
            OpenvSwitch().addFlow("echo {} | sudo ovs-ofctl add flow ovs ip,nw_src={},nw_dst={},priority=1,in_port={},actions=output:{}"
                                  .format(self.password, self.src, self.dst, self.interfaces[i], self.interfaces[i+1]))
