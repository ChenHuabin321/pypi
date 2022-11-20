# -*- coding: utf-8 -*-

from ._imports import *

class MysqlDao(object):
    def __init__(self, HOST, PORT, USER_NAME, PASSWORD, DB_NAME,
                 cursor_type=None, CHARSET='utf8'):
        self.conn = pymysql.connect(  # 创建数据库连接
            host=HOST,  # 要连接的数据库所在主机ip
            user=USER_NAME,  # 数据库登录用户名
            password=PASSWORD,  # 登录用户密码
            port=PORT,
            database=DB_NAME,
            charset=CHARSET  # 编码，注意不能写成utf-8
        )
        if cursor_type:
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
    def __init__(self, HOST, PORT, USER_NAME=None, PASSWORD=None, DB_NAME=None, COL_NAME=None):
        """
        HOST：服务器IP
        PORT：端口
        USER_NAME和PASSWORD：用户名和密码，为空时不进行密码验证
        DB_NAME：数据库名
        COL_NAME：集合名
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
    def __init__(self, db_name, db_pwd, db_conn, encoding="UTF-8"):
        self.conn = cx_Oracle.connect(db_name, db_pwd, db_conn, encoding)
        self.cur = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_trace):
        self.conn.commit()  # 提交事务
        self.cur.close()  # 关闭游标
        self.conn.close()  # 关闭数据库连接


class RedisDao(object):
    def __init__(self, redisDB=None, host=None, port=6379, password=None, db=0):
        """
        创建redis数据库连接
        """
        if redisDB:
            self.__db = redisDB
        else:
            redis_c = redis.StrictRedis(host=host, port=port,
                                        password=password,
                                        db=db)
            self.__db = redis_c

    def qsize(self, queue):
        return self.__db.llen(queue)  # 返回队列里面list内元素的数量

    def lput(self, queue, item):
        self.__db.lpush(queue, item)  # 添加新元素到队列最左方

    def rput(self, queue, item):
        self.__db.rpush(queue, item)  # 添加新元素到队列最右方

    def get_wait(self, queue, timeout=None):
        # 返回队列第一个元素，如果为空则等待至有元素被加入队列（超时时间阈值为timeout，如果为None则一直等待）
        item = self.__db.brpop(queue, timeout=timeout)
        if item:
            item = item[1]  # 返回值为一个tuple
        return item

    def get_nowait(self, queue):
        # 直接返回队列第一个元素，如果队列为空返回的是None
        item = self.__db.rpop(queue)
        return item

    def random_get(self, queue):
        """
        送队列中随机获取一个元素
        :param queue:
        :return:
        """
        length = self.__db.llen(queue)
        index = random.randint(0, length - 1)
        return self.__db.lindex(index)

    def get_len(self, queue):
        """
        获取queue的长度
        """
        return self.__db.llen(queue)
