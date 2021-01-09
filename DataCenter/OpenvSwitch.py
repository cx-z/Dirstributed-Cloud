# -*-coding:utf-8-*-
import os


class OpenvSwitch:
    def __init__(self) -> None:
        super().__init__()
        # 通过一个集合保存流表项
        self.ports = set()
        self.flows = set()

    def __del__(self) -> None:
        for item in self.flows:
            self.delFlow(item)
        self.flows.clear()
        for item in self.ports:
            self.delPort(item)
        self.ports.clear()

    def addPort(self, port: str, password: str, container="") -> None:
        os.system(
            "echo {} | sudo ovs-vsctl add-port ovs {} {}".format(password, port, container))
        self.ports.add(port)

    def delPort(self, port: str, password) -> None:
        os.system("echo {} | sudo ovs-vsctl del-port ovs {}".format(password, port))
        self.ports.remove(port)

    def addFlow(self, flow, password) -> None:
        os.system("echo {} | sudo ovs-vsctl add-flow ovs {}".format(password, flow))
        self.flows.add(flow)

    def delFlow(self, flow, password) -> None:
        os.system("echo {} | sudo ovs-vsctl del-flow ovs {}".format(password, flow))
        self.flows.remove(flow)
