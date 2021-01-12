# -*-coding:utf-8-*-
import os
import config


class OpenvSwitch:
    def __init__(self) -> None:
        super().__init__()
        # 通过一个集合保存流表项
        self.ports = set()
        self.flows = set()

    # def __del__(self) -> None:
    #     for item in self.flows:
    #         self.delFlow(item,config.PASSWORD)
    #     self.flows.clear()
    #     for item in self.ports:
    #         self.delPort(item,config.PASSWORD)
    #     self.ports.clear()

    def addPort(self, port: str, password: str, containerName="") -> None:
        os.system(
            "echo {} | sudo ovs-docker add-port ovs {} {}".format(password, port, containerName))
        self.ports.add(port)

    def delPort(self, port: str, password) -> None:
        os.system("echo {} | sudo ovs-vsctl del-port ovs {}".format(password, port))
        self.ports.remove(port)

    def addFlow(self, flow, password) -> None:
        print(flow)
        os.system("echo {} | sudo ovs-ofctl add-flow ovs {}".format(password, flow))
        self.flows.add(flow)

    def delFlow(self, flow, password) -> None:
        os.system("echo {} | sudo ovs-ofctl del-flow ovs {}".format(password, flow))
        self.flows.remove(flow)
