# -*- coding: utf-8 -*-
from chb._imports import *

from chb._log import Log

log = Log()()


class MysqlDao(object):
    """
    MySQL数据库的with上下文连接类。
    :param HOST: 主机地址
    :param PORT: 端口
    :param USER_NAME:用户名
    :param PASSWORD: 密码
    :param DB_NAME: 数据库名
    :param dictCursor: 是否字典型游标，True表示是，False表示创建一般游标。
    :param CHARSET: 字符集，默认为utf-8
    """
    def __init__(self, HOST, USER_NAME, PASSWORD, DB_NAME,PORT=3306,
                 dictCursor=False, CHARSET='utf8', **kwargs):
        """

        :param HOST:
        :param PORT:
        :param USER_NAME:
        :param PASSWORD:
        :param DB_NAME:
        :param cursor_type:
        :param CHARSET:
        """
        self.conn = pymysql.connect(  # 创建数据库连接
            host=HOST,  # 要连接的数据库所在主机ip
            user=USER_NAME,  # 数据库登录用户名
            password=PASSWORD,  # 登录用户密码
            port=PORT,
            database=DB_NAME,
            charset=CHARSET  # 编码，注意不能写成utf-8
        )
        if dictCursor:
            self.cursor = self.conn.cursor(pymysql.cursors.DictCursor)
        else:
            self.cursor = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_trace):
        self.conn.commit()  # 提交事务
        self.cursor.close()  # 关闭游标
        self.conn.close()  # 关闭数据库连接


class MongoDao(object):
    """
    MongoDB 数据库的with上下文连接类。
    HOST：服务器IP
    PORT：端口，默认27017
    USER_NAME和PASSWORD：用户名和密码，为空时不进行密码验证
    DB_NAME：数据库名
    COL_NAME：集合名
    """
    def __init__(self, HOST, PORT=27017, USER_NAME=None, PASSWORD=None, DB_NAME=None, COL_NAME=None, **kwargs):
        """
        HOST：服务器IP
        PORT：端口
        USER_NAME和PASSWORD：用户名和密码，为空时不进行密码验证
        DB_NAME：数据库名，为None时，表示不连接指定DB
        COL_NAME：集合名，为None时，表示不连接指定集合
        """

        if USER_NAME and PASSWORD:
            self.client = pymongo.MongoClient(host=HOST, port=PORT, username=USER_NAME, password=PASSWORD,
                                              connect=False)
        else:
            self.client = pymongo.MongoClient(host=HOST, port=PORT, connect=False)

        if DB_NAME:
            self.db = self.client[DB_NAME]
            if COL_NAME:
                self.col = self.db[COL_NAME]
            else:
                self.col = None
        else:
            self.db = None
            self.col = None

    def find(self, filters=None, fields=None):
        """
        filter：查询条件
        fields：需要返回的字段
        """
        assert self.col is not None, "集合不能为None！"
        if filters is None:
            filters = {}
        if fields is None:
            fields = {'_id': 0}
        return [i for i in self.col.find(filters, fields)]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_trace):
        self.client.close()  # 关闭数据库连接


class OracleDao(object):
    """
    Oracle数据库的with上下文连接类。
    :param db_name: 数据库名
    :param db_pwd: 密码
    :param db_conn: 数据库连接字符串
    :param encoding: 编码，默认为utf-8
    """
    def __init__(self, db_name, db_pwd, db_conn, encoding="UTF-8", **kwargs):
        """
        :param db_name: 数据库名
        :param db_pwd: 密码
        :param db_conn: 数据库连接字符串，例如："192.168.1.110:1521/testdb"
        :param encoding: 编码，默认为utf-8
        """
        self.conn = cx_Oracle.connect(db_name, db_pwd, db_conn, encoding=encoding)
        self.cur = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_trace):
        self.conn.commit()  # 提交事务
        self.cur.close()  # 关闭游标
        self.conn.close()  # 关闭数据库连接

    def fetchmany(self, num_row):
        """
        对原生fetchmany进一步封装为生成器，可以通过for循环直接遍历
        :param num_row: 每次循环取出的数据量
        :return: list列表
        """
        self.cur.arraysize = num_row
        self.cur.prefetchrows = num_row
        while True:
            rows = self.cur.fetchmany(num_row)
            if not rows:
                break
            yield rows


class RedisDao(object):
    """
    Redis数据库的with上下文管理连接。
    :param redisDB: redis.StrictRedis对象，现有的redis连接。当传递该对象时，后续的host、post等参数无效。
    :param host: redis主机地址
    :param port: redis端口，默认为6379
    :param password: 密码
    :param db: 数据库序号，默认为0
    """
    def __init__(self, redisDB=None, host=None, port=6379, password=None, db=0, **kwargs):
        """
        创建redis数据库连接
        :param redisDB: redis.StrictRedis对象，现有的redis连接。当传递该对象时，后续的host、post等参数无效。
        :param host: redis主机地址
        :param port: redis端口
        :param password: 密码
        :param db: 数据库序号
        """
        if redisDB:
            self.db = redisDB
        else:
            self.db = redis.StrictRedis(host=host, port=port,
                                        password=password,
                                        db=db)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_trace):
        self.db.close()

    def qsize(self, queue):
        return self.db.llen(queue)  # 返回队列里面list内元素的数量

    def lput(self, queue, item):
        self.db.lpush(queue, item)  # 添加新元素到队列最左方

    def rput(self, queue, item):
        self.db.rpush(queue, item)  # 添加新元素到队列最右方

    def lget_wait(self, queue, timeout=None):
        # 返回队列第最左侧元素，如果为空则等待至有元素被加入队列（超时时间阈值为timeout，如果为None则一直等待）
        item = self.db.blpop(queue, timeout=timeout)
        if item:
            item = item[1]  # 返回值为一个tuple
        return item

    def get_wait(self, queue, timeout=None):
        # 返回队列最右侧元素，如果为空则等待至有元素被加入队列（超时时间阈值为timeout，如果为None则一直等待）
        item = self.db.brpop(queue, timeout=timeout)
        if item:
            item = item[1]  # 返回值为一个tuple
        return item

    def set_key(self, key, value):
        """
        设置键值对
        :param key: 键名
        :param value: 值
        :return: Boolean
        """
        return self.db.set(key, value)

    def get_nowait(self, queue):
        # 直接返回队列第一个元素，如果队列为空返回的是None
        item = self.db.rpop(queue)
        return item

    def lget_nowait(self, queue):
        # 直接返回队列第一个元素，如果队列为空返回的是None
        item = self.db.lpop(queue)
        return item

    def random_get(self, queue):
        """
        送队列中随机获取一个元素
        :param queue:
        :return:
        """
        length = self.db.llen(queue)
        index = random.randint(0, length - 1)
        return self.db.lindex(index)

    def get_len(self, queue):
        """
        获取queue的长度
        """
        return self.db.llen(queue)

    def hset(self, set_name, key, value):
        """
        向名为set_name的hash队列中添加一个键值对
        """
        self.db.hset(set_name, key, value)

    def hget(self, set_name, key):
        """
        从名为set_name的hash队列中获取一个键值对
        """
        return self.db.hget(set_name, key)

    def sadd(self, set_name, value):
        """
        向名为set_name的set中添加一个元素value
        """
        self.db.sadd(set_name, value)

    def srem(self, set_name, value):
        """
        向名为set_name的set中删除一个元素value
        """
        self.db.srem(set_name, value)

    def inset(self, set_name, value):
        """
        判断元素value是否在名为set_name的set中
        """
        self.db.sismember(set_name, value)
