#-*-coding:utf-8-*-


class Request:
    def __init__(self) -> None:
        super().__init__()
        self.id:int = 0
        self.src:str = ""
        self.dst:str = ""
        self.sfc:list = list() # sfc是一个列表，依次存储着每个vnf的类型
        self.bandwidth:int = 0
        self.duration = "" # 持续时间，后面补
        self.bid:float = 0
        self.maxDelay:int = 0
        self.offtime:float = 0

    def __lt__(self, other):
        if self.offtime < other.offtime:
            return True
        else:
            return False

