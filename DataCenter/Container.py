# -*-coding:utf-8-*-
import os
from OpenvSwitch import OpenvSwitch


# 获取本机所有网卡，这样比较ovs-docker给容器添加网卡前后，本机多出来的网卡就对应新网卡
def getAllEth() -> set:
    eths = set()
    for iface in os.listdir('/sys/class/net'):
        eths.add(iface)
    return eths


class Container:
    def __init__(self, name, type, cpu = "", mem ="") -> None:
        super().__init__()
        self.name: str = name
        self.type: str = type
        self.cpu: float = cpu  # cpu百分比，单位是微秒
        self.mem: float = mem  # 内存大小
        self.eth1: str = ""  # 容器网卡eth1在bridge上的vethpair
        self.eth2: str = ""  # 容器网卡eth2在bridge上的vethpair

    # 根据容器名给指定容器添加流量进出的网卡eth1和eth2
    # 并配置流表项，将流量从eth1引导至eth2
    def addInterfaceToContainer(self, password: str) -> None:
        ethsBefore = getAllEth()
        # 每个VNF需要两张网卡，流量流入eth1
        OpenvSwitch().addPort("eth1", password, self.name)
        # os.system(
        #     "echo {} | sudo ovs-docker add-port ovs eth1 {}".format(password, container.name))
        for iface in os.listdir('/sys/class/net'):
            if iface not in ethsBefore:
                print("eth1's vethpair is"+iface)
                self.eth1 = iface
                ethsBefore.add(iface)
                break
        OpenvSwitch().addPort("eth2", password, self.name)
        for iface in os.listdir('/sys/class/net'):
            if iface not in ethsBefore:
                print("eth2's vethpair is"+iface)
                self.eth2 = iface
                break
        # # 启动容器内引导流量的ovs交换机和对应的流表
        # 删除容器内名为bridge的ovs交换机的默认流表项
        os.system("docker exec -it {} /bin/bash -c \'ovs-ofctl del-flows bridge\'".format(self.name))
        # 将网卡eth1和eth2连接到bridge
        os.system("docker exec -it {} /bin/bash -c \'ovs-vsctl add-port bridge eth1\'".format(self.name))
        os.system("docker exec -it {} /bin/bash -c \'ovs-vsctl add-port bridge eth2\'".format(self.name))

        # 配置从eth1到eth2的流表项
        os.system("docker exec -it {} /bin/bash -c \'ovs-ofctl add-flow bridge priority=1,in_port=eth1,actions=output:eth2\'".format(self.name))
        print("")
        
    def createContainers(self):
        print("启动容器"+self.name)
        os.system("docker run -itd --privileged=true -m={} --cpus={} --name={} {}"
                  .format(self.mem, self.cpu, self.name, self.type))
        os.system("docker exec -it {} /bin/bash -c \'/usr/share/openvswitch/scripts/ovs-ctl start\'".format(self.name))

