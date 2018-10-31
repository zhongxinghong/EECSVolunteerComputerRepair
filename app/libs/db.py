#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# filename: app/libs/db.py


import os
import sqlite3
from collections import OrderedDict

try:
    from .utils import iter_flat
except ImportError:
    from utils import iter_flat


Root_Dir = os.path.join(os.path.dirname(__file__), "../")
Data_Dir = os.path.join(Root_Dir, "data/")


__all__ = [
    "OrderDB",
    # "AdminDB",
]


class SQLiteDB(object):

    dbName = "data"

    Dict_Row   = lambda cur,row: dict(zip([col[0] for col in cur.description],row))
    Single_Raw = lambda cur,row: row[0]

    def __init__(self):
        if self.dbName == "":
            raise NotImplementedError
        self.con = sqlite3.connect(os.path.join(Data_Dir, "{}.db".format(self.dbName)))

    def __enter__(self):
        return self

    def __exit__(self, type, value, trace):
        self.close()


    @property
    def cur(self):
        cur = self.con.cursor()
        cur.row_factory = self.__class__.Dict_Row
        return cur

    @property
    def single_cur(self):
        cur = self.con.cursor()
        cur.row_factory = self.__class__.Single_Raw
        return cur

    @property
    def origin_cur(self):
        return self.con.cursor()


    def execute(self, *args, **kwargs):
        return self.cur.execute(*args, **kwargs)

    def executemany(self, *args, **kwargs):
        return self.cur.executemany(*args, **kwargs)

    def commit(self, *args, **kwargs):
        return self.con.commit(*args, **kwargs)

    def close(self):
        self.con.close()


    def rebuild(self, *args, **kwargs):
        raise NotImplementedError

    def select(self, table, cols=[], where=None, args=[]):
        sql = "SELECT %s FROM %s \n" % (",".join(cols), table)
        if where is not None:
            sql += "WHERE %s" % where
        return self.cur.execute(sql, args)

    def select_join(self, cols, key):
        """ cols = [
                ["newsInfo",("newsID","title","masssend_time AS time")], # 可别名
                ["newsDetail",("column","in_use")],
                ["newsContent",("content","newsID")] # 可重复 key
            ]
            key = "newsID"
        """

        fields = [[table, ['.'.join([table,col]) for col in _cols]] for table, _cols in cols]

        cols = iter_flat([_cols for table, _cols in fields])

        table0, cols0 = fields.pop(0)

        sql = "SELECT {cols} FROM {table0} \n".format(cols=','.join(cols),table0=table0)
        for table in [table for table,cols in fields]:
            sql += "INNER JOIN {table} ON {key0} == {key} \n".format(
                        table = table,
                        key0 = '.'.join([table0, key]),
                        key = '.'.join([table, key])
                    )

        return self.cur.execute(sql)

    def insert_one(self, table, dataDict):
        k,v = tuple(zip(*dataDict.items()))
        with self.con:
            cur = self.con.execute("INSERT OR REPLACE INTO %s (%s) VALUES (%s)"
                % (table, ",".join(k), ",".join('?'*len(k))), v)
            self.con.commit()
        return cur

    def insert_many(self, table, dataDicts):
        dataDicts = [OrderedDict(sorted(dataDict.items())) for dataDict in dataDicts]
        k = dataDicts[0].keys()
        vs = [tuple(dataDict.values()) for dataDict in dataDicts]
        with self.con:
            cur = self.con.executemany("INSERT OR REPLACE INTO %s (%s) VALUES (%s)"
                % (table, ",".join(k), ",".join('?'*len(k))), vs)
            self.con.commit()
        return cur


class OrderDB(SQLiteDB):

    def create_table(self, table, rebuild=False):
        try:
            if rebuild:
                self.con.execute("DROP TABLE IF EXISTS %s" % table)
                self.con.commit()
            if table == "orders": # 订单信息 （不可用 order 保留字！）
                self.con.execute("""CREATE TABLE IF NOT EXISTS %s
                    (
                        orderID        INTEGER  PRIMARY KEY AUTOINCREMENT,
                        status         INT      NOT NULL,  -- 订单状态（是否有效？ 0 -- 有效； 1 -- 已撤回）
                        email          TEXT     NOT NULL,  -- 联系邮箱
                        wechat         TEXT     NOT NULL,  -- 微信号
                        model          TEXT     NOT NULL,  -- 电脑型号
                        type           TEXT     NOT NULL,  -- 问题类型
                        description    TEXT     NOT NULL,  -- 问题描述
                        day            DATE     NOT NULL,  -- 预约时间
                        site           TEXT     NOT NULL,  -- 活动地点
                        appointment    TEXT     NOT NULL,  -- 预约时段
                        create_time    INT      NOT NULL   -- 创建时间
                    )
                """ % table)
            elif table == "queue": # 维修队列
                self.con.execute("""CREATE TABLE IF NOT EXISTS %s
                    (
                        queueID        INTEGER  PRIMARY KEY AUTOINCREMENT,
                        orderID        INT      NOT NULL,
                        status         INT      NOT NULL,  -- 维修状态（是否已维修？ 0 -- 未维修； 1 -- 正在维修； 2 -- 已维修）
                        create_time    INT      NOT NULL,  -- 创建时间
                        FOREIGN KEY (orderID) REFERENCES orders(orderID)
                    )
                """ % table)
            else:
                raise ValueError
            self.con.commit()
        except Exception as err:
            self.con.rollback()
            raise err


'''
class AdminDB(SQLiteDB):

    def create_table(self, table, rebuild=False):
        try:
            if rebuild:
                self.con.execute("DROP TABLE IF EXISTS %s" % table)
                self.con.commit()
            if table == "admins":
                self.con.execute("""CREATE TABLE IF NOT EXISTS %s
                    (
                        account     TEXT        PRIMARY KEY NOT NULL,
                        password    CHAR(32)    NOT NULL,  -- 密码的 MD5
                    )
                    """)
        except Exception as err:
            self.con.rollback()
            raise err
'''