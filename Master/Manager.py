# -*-coding:utf-8-*-
"""
本文件负责将正在运行的请求相关信息保存在数据库
同时将下线的请求的信息从数据库中删除
并且修改各个节点的内存和cpu信息
修改各条链路的带宽信息
"""
import pymysql
import config
from DataCenter import DataCenter
from Edge import Edge
from Request import Request
from VNF import VNF
from Singleton import Singleton


class Manager(metaclass = Singleton):
    def __init__(self) -> None:
        super().__init__()
        self.requests: list = list()
        self.nodes: set = set()
        self.edges: set = set()
        self.db = pymysql.connect(
            "localhost", "root", config.PASSWORD, config.DATABASE)
        self.create_table()

    def __del__(self) -> None:
        cursor = self.db.cursor()
        cursor.execute("DROP TABLE IF EXISTS Requests")
        cursor.execute("DROP TABLE IF EXISTS VNFs")
        sql = """UPDATE DataCenters SET 
            leftmem = {}, leftcpu = {}, current_income = {}"""\
            .format(config.INIT_MEMORY, config.INIT_CPU, config.INIT_INCOME)
        self.exec_sql(sql)
        sql = """UPDATE Edges SET 
            leftbandwidth = {}, current_income = {}"""\
            .format(config.INIT_BANDWIDTH, config.INIT_INCOME)
        self.exec_sql(sql)

    # 在数据库Master创建表格Requests和VNFs
    def create_table(self) -> None:
        cursor = self.db.cursor()
        cursor.execute("USE Master")
        cursor.execute("DROP TABLE IF EXISTS Requests")
        sql = """CREATE TABLE IF NOT EXISTS Requests(
                id INT NOT NULL,
                source CHAR(20),
                destination CHAR(20),
                sfc CHAR(100),
                bandwidth INT,
                maxDelay INT，
                duration INT,
                bid INT，
                PRIMARY KEY (id)
            )"""
        cursor.execute(sql)
        cursor.execute("DROP TABLE IF EXISTS VNFs")
        sql = """CREATE TABLE IF NOT EXISTS VNFs(
                sfc_id INT NOT NULL,
                type INT(20),
                sequence INT(20),
                memory FLOAT(6,2),
                cpu FLOAT,
                dc_id INT,
                PRIMARY KEY (sfc_id,sequence)
            )"""
        cursor.execute(sql)

    # 执行某条SQL语句，返回输出结果
    def exec_sql(self, sql:str) -> tuple:
        # 本工程的信息保存在数据库Master中
        self.db.cursor().execute("USE Master")
        try:
            self.db.cursor().execute(sql)
            results = self.db.cursor().fetchall()
            return results
        except:
            print("execute {} error".format(sql))
            self.db.rollback()
            return ()

    # 更新数据库的表DataCenters中某节点的信息
    def update_node_info(self, node: DataCenter) -> None:
        sql = """UPDATE DataCenters SET
            leftmem = {}, leftcpu = {} , current_income = {}
            WHERE id = {}"""\
            .format(node.leftmem, node.leftcpu, node.current_income, node.id)
        self.exec_sql(sql)

    # 从数据库的表DataCenters中读取某节点的信息
    def load_node_info(self, node: DataCenter) -> None:
        sql = """SELECT * FROM DataCenters
            WHERE id={}""".format(node.id)
        dc: tuple = self.exec_sql(sql)
        if not dc:
            return
        node.leftmem = dc[3]
        node.leftcpu = dc[4]
        node.current_income = dc[5]

    # 更新数据库的表Edges中某链接的信息
    def update_edge_info(self, edge: Edge) -> None:
        sql = """UPDATE Edges SET
            leftbandwidth = {}, current_income = {}
            WHERE endpoint1 = {} AND endpoint2 = {}"""\
            .format(edge.leftBandWidth, edge.current_income, edge.endpoint1, edge.endpoint2)
        self.exec_sql(sql)

    # 从数据库的表Edges中读取某链接的信息
    def load_edge_info(self, edge: Edge) -> None:
        sql = """SELECT * FROM Edges
            WHERE endpoint1={} and endpoint2={}"""\
            .format(edge.endpoint1, edge.endpoint2)
        e: tuple = self.exec_sql(sql)
        if not e:
            return
        edge.propagationDelay = e[2]
        edge.totalBandWidth = e[3]
        edge.leftBandWidth = e[4]
        edge.unitprice = e[5]
        edge.current_income = e[6]

    # 向数据库的表Requests中插入新上线的请求
    def insert_request_info(self, req: Request) -> None:
        sfc:str = ""
        for v in req.sfc:
            str += v + ' '
        sql = """INSERT INTO Requests(id, source, destination, sfc, bandwidth, maxDelay, duration, bid)
            VALUES({}, '{}', '{}', '{}', {}, {}, {}, {})"""\
            .format(req.id, req.src, req.dst, sfc, req.bandwidth, req.maxDelay, req.duration, req.bid)
        self.exec_sql(sql)

    # 从数据库的表Requests中读取某个在线的请求信息
    def load_request_info(self, req: Request) -> None:
        sql = """SELECT * FROM Requests WHERE id = {}"""\
            .format(req.id)
        r:tuple = self.exec_sql(sql)
        if not r:
            return
        req.src = r[1]
        req.dst = r[2]
        req.sfc = r[3].split(' ')
        req.bandwidth = r[4]
        req.maxDelay = r[5]
        req.duration = r[6]
        req.bid = r[7]

    # 从数据库的表Requests中删除下线的请求
    def del_request_info(self, req: Request) -> None:
        sql = """DELETE FROM Requests WHERE id = {}"""\
            .format(req.id)
        self.exec_sql(sql)

    # 将新的VNF插入数据库的表VNFs中
    def insert_vnf_info(self, vnf: VNF) -> None:
        sql = """INSERT INTO VNFs(sfc_id, type, sequence, memory, cpu, dc_id)
            VALUES({}, {}, {}, {}, {}, {})"""\
            .format(vnf.sfc_id, vnf.type, vnf.sequence, vnf.memory, vnf.cpu, vnf.dc_id)
        self.exec_sql(sql)

    # 从数据库中读取某VNF信息
    def load_vnf_info(self, vnf: VNF) -> None:
        sql = """SELECT * FROM VNFs WHERE sfc_id = {} and sequence = {}"""\
            .format(vnf.sfc_id, vnf.sequence)
        v:tuple = self.exec_sql(sql)
        if not v:
            return
        vnf.type = v[1]
        vnf.memory = v[3]
        vnf.cpu = v[4]
        vnf.dc_id = v[5]

    # 从数据库中删除某VNF信息
    def del_vnf_info(self, vnf: VNF) -> None:
        sql = """DELETE FROM VNFs WHERE sfc_id = {} and sequence = {}"""\
            .format(vnf.id, vnf.sequence)
        self.exec_sql(sql)
