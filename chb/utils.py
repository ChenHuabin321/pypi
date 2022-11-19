# -*- coding: utf-8 -*-
import os
import time
import queue
from threading import Thread
from log import Log


logger = Log().getLogger()


def get_current_path():
    """
    获取当前文件所在目录完整路径
    """
    return os.path.abspath(os.path.dirname('.'))


def get_time_str(format='%Y%m%d%H%M%S'):
    """
    按指定格式获取当前时间字符串

    %y 两位数的年份表示（00-99）
    %Y 四位数的年份表示（000-9999）
    %m 月份（01-12）
    %d 月内中的一天（0-31）
    %H 24小时制小时数（0-23）
    %I 12小时制小时数（01-12）
    %M 分钟数（00=59）
    %S 秒（00-59）
    %a 本地简化星期名称
    %A 本地完整星期名称
    %b 本地简化的月份名称
    %B 本地完整的月份名称
    %c 本地相应的日期表示和时间表示
    %j 年内的一天（001-366）
    %p 本地A.M.或P.M.的等价符
    %U 一年中的星期数（00-53）星期天为星期的开始
    %w 星期（0-6），星期天为星期的开始
    %W 一年中的星期数（00-53）星期一为星期的开始
    %x 本地相应的日期表示
    %X 本地相应的时间表示
    %Z 当前时区的名称
    %% %号本身
    """
    return time.strftime(format, time.localtime(time.time()))


class MutilThreadReader:
    """
    本类是一个装饰器用于使用单线程IO操作函数改为多线程方式执行。

    例如在传统（单线程）方式下，读取全省各地区的excel文件，我们先定义好读取单个文件并处理数据方法函数func，然后需要通过for循环遍历。
    在多线程情况下（本方法中），通过func和所有excel文件完整路径组成的list传入到本方法中，本方法会通过多线程方式调用func方法，并将最终结果存放在一个list中返回。

    示例：read_excel(path)为读取当个excel的函数，path为单个excel完整路径，但此时有多个excel需要读取，正常情况需要使用for需要，调用read_excel函数，这种方式使用单线程，效率低。
    改进方案：定义read_excel(path)函数时，使用MutilThreadReader装饰器进行装饰。注意，使用MutilThreadReader装饰器是，需要给MutilThreadReader传两个参数，第一个是所有excel文件完整路径组成的list
            第二个是启动线程数量

    定义read_excel(path)过程如下：

        @MutilThreadReader(['./规划库/excel文件1.xlsx', './规划库/excel文件2.xlsx', './规划库/excel文件3.xlsx'], 3)
        def read_excel(path):
            pass
    """

    def __init__(self, *args):
        """
        args[0]：多线程遍历的资源，即所有地局的excel路径组成的list
        args[1]：启动多少个线程，为None时是文件数量除以3再加上1个
        """
        path_lst = args[0]
        thread_num = args[1]
        self.thread_num = thread_num if thread_num else len(lst) // 3 + 1
        self.q1 = queue.Queue()  # 存放所有需要遍历的文件的队列
        self.q2 = queue.Queue()  # 存放每一次读取结果的队列
        for item in path_lst:
            self.q1.put(item)

    def inner(self, func):
        """
        从文件队列中取出文件，调用func方法函数进行读取，并将结果存放到结果队列中
        """
        while True:
            try:
                file = self.q1.get_nowait()
                logger.info(f'开始读取: {file}')
                df = func(file)
                logger.info(f'完成读取: {file}')
                self.q2.put(df)
            except queue.Empty:
                logger.info('队列已空1……')
                break

    def __call__(self, func):
        """
        多线程实现函数，装饰器
        """

        def real_run():
            p_list = []
            start = time.time()
            for i in range(self.thread_num):
                p = Thread(target=self.inner, args=(func,))
                p.start()
                p_list.append(p)

            for p in p_list:
                p.join()
            end = time.time()
            logger.info(f'共历时: {end - start}秒')
            result = []
            while True:
                try:
                    df = self.q2.get_nowait()
                    result.append(df)
                except queue.Empty:
                    break
            return result

        real_run.__doc__ = MutilThreadReader.__doc__  # 将装饰后的函数文档，修改文装饰器类的文档
        return real_run


class Tableprint:
    """
    本类作用与prettytable 类似，用于打印类似于下方的表格，区别在于，本类可以实现增量式打印，每次添加打印一行
    +------------+----------+----------+--------------------+-----------------+
    |   epoch    |   mode   |   loss   |      accuracy      |     is_best     |
    +------------+----------+----------+--------------------+-----------------+
    |     0      |  train   |  0.4911  |       0.8566       |                 |
    +------------+----------+----------+--------------------+-----------------+
    |     0      |   test   |  0.3546  |       0.9216       |       True      |
    +------------+----------+----------+--------------------+-----------------+
    """
    def __init__(self, headers, align='^', pad_len=6):
        """
        :param headers: 表头
        :param align: 对齐方式
        :param pad_len: 每一列的填充长度
        """
        self.padding_lenth = []
        headers = [str(h) for h in headers]
        for i, h in enumerate(headers):
            count = 0  # 中文字符数量
            for word in h:
                if (word >= '\u4e00' and word <= '\u9fa5') or word in ['；', '：', '，', '（', '）', '！', '？', '——', '……',
                                                                       '、', '》', '《']:
                    count += 1
            size = len(h) + count
            padding_size = size + pad_len if size < 15 else int(size * 1.5)
            self.padding_lenth.append(padding_size if padding_size else padding_size + 1)
        row_line_tmp = '+'.join([f'{"":-{align}{p}}' for p in self.padding_lenth])
        self.row_line = f"+{row_line_tmp}+"  # 每一行的线
        self.header_line = self.row_line.replace('-', '=')  # 表头的线
        # self.row_line = f"+{'+'.join([''.center(p, '-') for p in self.padding_lenth])}+"  # 每一行的线
        # self.header_content = f"|{'|'.join([h.center(self.string_len(h, p), ' ') for h, p in zip(headers, self.padding_lenth)])}|"
        header_content_tmp = '|'.join([f'{h:{align}{self.string_len(h, p)}}' for h, p in zip(headers, self.padding_lenth)])
        self.header_content = f"|{header_content_tmp}|"

    def string_len(self, string, width):
        """
        获取填充后字符串宽度（不是字符串长度）
        :param string: 字符串内容
        :param width: 总长度
        :return: 最后宽度
        """
        try:
            count = 0  # 长宽度中文字符数量
            for word in str(string):  # 检测长宽度中文字符
                if (word >= '\u4e00' and word <= '\u9fa5') or word in ['；', '：', '，', '（', '）', '！', '？', '——',
                                                                        '……','、', '》', '《']:
                    count += 1
            width = width - count if width >= count else 0
            return width
        except:
            logger.warn('函数参数输入错误！')

    def print_header(self):
        """打印输出表头"""
        print(self.header_line)
        print(self.header_content)
        print(self.header_line)

    def print_row(self, *row_lst):
        """打印输出一行"""
        assert len(row_lst) == len(self.padding_lenth), '行字段数量必须与表头一致！'
        strings = []
        for field, size in zip(row_lst, self.padding_lenth):
            strings.append(
                str(field).center(self.string_len(field, size), ' ')
            )
        line_content = '|'.join(strings)
        line_content = f"|{line_content}|"
        print(line_content)
        print(self.row_line)