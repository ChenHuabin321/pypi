# -*- coding: utf-8 -*-
from __future__ import print_function

from collections.abc import Iterable
import pytz
from threading import Thread
from chb._log import log
from datetime import datetime

import sys
from itertools import chain
from collections import deque
try:
    from reprlib import repr
except ImportError:
    pass
from chb._imports import *
# log = Log(message_only=True)()


def set_device(cuda_index=0):
    """
    torch建模时，设置设备类型：CPU 或 GPU
    cuda_index ：GPU 索引，默认为0
    """
    device = torch.device(f"cuda:{cuda_index}" if torch.cuda.is_available() else "cpu")
    log(f'Succeed to set device: {device}')
    return device


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


class MutilThreadReader(object):
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
        self.thread_num = thread_num if thread_num else len(path_lst) // 3 + 1
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
                log(f'开始读取: {file}')
                df = func(file)
                log(f'完成读取: {file}')
                self.q2.put(df)
            except queue.Empty:
                log('队列已空1……')
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
            log(f'共历时: {end - start}秒')
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


class Tableprint(object):
    """
    本类作用与prettytable 类似，用于打印类似于下方的表格，区别在于，本类可以实现增量式打印，每次添加打印一行
    +------------+----------+----------+--------------------+-----------------+
    |   epoch    |   mode   |   loss   |      accuracy      |     is_best     |
    +------------+----------+----------+--------------------+-----------------+
    |     0      |  train   |  0.4911  |       0.8566       |                 |
    +------------+----------+----------+--------------------+-----------------+
    |     0      |   test   |  0.3546  |       0.9216       |       True      |
    +------------+----------+----------+--------------------+-----------------+

    :param headers: 表头
    :param align: 对齐方式
    :param pad_len: 每一列的填充长度
    :param print_index: 是否打印序号列
    :param index_name: 序号列的列名
    """
    def __init__(self, headers, align='^', pad_len=6, print_index=False, index_name='index'):
        """
        :param headers: 表头
        :param align: 对齐方式
        :param pad_len: 每一列的填充长度
        :param print_index: 是否打印序号列
        :param index_name: 序号列的列名
        """
        self.align = align
        self.padding_lenth = []
        self.col_num = len(headers)
        headers = [str(h) for h in headers]
        if print_index:
            self.index = 0

            headers.insert(0, index_name)
        for i, h in enumerate(headers):
            count = 0  # 中文字符数量
            for word in h:
                if (word >= '\u4e00' and word <= '\u9fa5') or word in ['；', '：', '，', '（', '）', '！', '？', '——', '……',
                                                                       '、', '》', '《']:
                    count += 1
            size = len(h) + count
            padding_size = size + pad_len if size < 15 else int(size * 1.5)
            self.padding_lenth.append(padding_size if padding_size else padding_size + 1)
        row_line_tmp = '+'.join([f'{"":-{self.align}{p}}' for p in self.padding_lenth])
        self.row_line = f"+{row_line_tmp}+"  # 每一行的线
        self.header_line = self.row_line.replace('-', '=')  # 表头的线
        header_content_tmp = '|'.join([f'{h:{self.align}{self.string_len(h, p)}}' for h, p in zip(headers, self.padding_lenth)])
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
            log.warn('函数参数输入错误！')

    def print_header(self):
        """打印输出表头"""
        print(self.header_line)
        print(self.header_content)
        print(self.header_line)

    def print_middle_info(self, info):
        """
        在不影响表结构情况下，在打印每行结果前需要输出的信息
        :param info: 需要输出的信息
        :return:
        """
        print(f'\r{info}', end='')

    def print_row(self, *row_lst):
        """打印输出一行"""
        assert len(row_lst) == self.col_num, '行字段数量必须与表头一致！'
        row_lst2 = []
        for i in row_lst:
            if isinstance(i, torch.Tensor) or isinstance(i, float):
                row_lst2.append(f"{i:.4f}")
            else:
                row_lst2.append(str(i))
        if hasattr(self, 'index'):
            self.index += 1
            row_lst2.insert(0, self.index)
        strings = []
        for field, size in zip(row_lst2, self.padding_lenth):
            strings.append(
                f'{str(field):{self.align}{self.string_len(field, size)}}'
            )
        line_content = '|'.join(strings)
        line_content = f"\r|{line_content}|"
        print(line_content)
        print(self.row_line)


def getsizeof(data):
    """
    自适应输出变量占用内存大小
    data：变量
    示例：getsizeof(data)  # 返回： 1 G 10 M 104 KB'
    """
    size = sys.getsizeof(data)
    g = f"{int(size // (1024**3)):d} G " if size // (1024**3) else ""
    m = f"{int(size % (1024**3) // (1024**2)):d} M " if size % (1024**3) // (1024**2) else ""
    kb = f"{round(size % (1024**3) % 1024, 5)} KB" if size % (1024**3) % 1024 else ""
    return f"{g}{m}{kb}"


def getdeepsizeof(o, handlers={}, verbose=False):
    """
    获取Python对象大致占用内存空间大小，注意本方法可以获取集合元素深层嵌套的占用空间总和，但集合元素越多，效率越低
    """
    dict_handler = lambda d: chain.from_iterable(d.items())
    all_handlers = {tuple: iter,
                    list: iter,
                    deque: iter,
                    dict: dict_handler,
                    set: iter,
                    frozenset: iter,
                    }
    all_handlers.update(handlers)  # user handlers take precedence
    seen = set()  # track which object id's have already been seen
    default_size = getsizeof(0)  # estimate sizeof object without __sizeof__

    def sizeof(o):
        if id(o) in seen:  # do not double count the same object
            return 0
        seen.add(id(o))
        s = sys.getsizeof(o, default_size)
        for typ, handler in all_handlers.items():
            if isinstance(o, typ):
                s += sum(map(sizeof, handler(o)))
                break
        return s

    size = sizeof(o)
    g = f"{int(size // (1024 ** 3)):d} G " if size // (1024 ** 3) else ""
    m = f"{int(size % (1024 ** 3) // (1024 ** 2)):d} M " if size % (1024 ** 3) // (1024 ** 2) else ""
    kb = f"{round(size % (1024 ** 3) % 1024, 5)} KB" if size % (1024 ** 3) % 1024 else ""
    return f"{g}{m}{kb}"


class Timer:
    """
        计时器，统计一段代码的运行时长
        使用方法：
        with Timer():
            pass
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

    def __init__(self, name=None):
        self.start_time = None
        self.name = name

    def __enter__(self):
        self.start_time = time.time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        info = self.time_cost(self.start_time, time.time())
        if self.name is not None:
            log(f'Time Cost-{self.name}: {info}')
        else:
            log(f'Time Cost: {info}')

    @staticmethod
    def time_cost(start_time, end_time):
        """
        自适应输出时间消耗
        start_time：开始时间，时间戳，整型
        end_time：结束时间，时间戳，整型
        示例：time_cost(0, 3668)  # 返回： 1h 1m 8s
        """
        cost = end_time - start_time
        h = f"{int(cost // 3600):d} h " if cost // 3600 else ""
        m = f"{int(cost % 3600 // 60):d} m " if cost % 3600 // 60 else ""
        s = f"{round(cost % 3600 % 60, 5)} s" if cost % 3600 % 60 else ""
        return f"{h}{m}{s}"

    @staticmethod
    def stamp2str(timestamp, format_str='%Y-%m-%d %H:%M:%S', timezone='UTC'):
        """
        将整型时间戳转换为指定格式的时间字符串
        :param timestamp: 整型，时间戳
        :param format_str: 字符型， 输出时间字符串的格式，默认 %Y-%m-%d %H:%M:%S
        :param timezone: 字符型， 时区，默认为 UTC 也可以设置为  CST
        :return:  指定格式的时间字符串
        """
        if timezone == 'UTC':
            st = time.gmtime(timestamp)  # UTC时区
        else:
            st = time.localtime(timestamp)  # CST时区
        return time.strftime(format_str, st)

    @staticmethod
    def str2stamp(string, format_str='%Y-%m-%d %H:%M:%S', timezone='UTC'):
        """
        将指定格式的时间字符串转化为整型时间戳
        :param string:  时间字符串
        :param format_str: 字符型， string参数的时间格式
        :param timezone: 字符型， 时区，默认为 UTC 也可以设置为  CST
        :return:  整型时间戳
        """
        # 转换为struct_time对象
        st = time.strptime(string, format_str)
        if timezone == 'UTC':
            return int(time.mktime(st) - time.timezone)  # UTC时区
        else:
            return int(time.mktime(st))  # CST时区

    @staticmethod
    def get_time_str(format='%Y%m%d%H%M%S'):
        """
        按指定格式获取当前时间字符串
        :param format: 输出时间字符串的格式，默认为  %Y%m%d%H%M%S
        :return: 时间字符串
        """
        return time.strftime(format, time.localtime(time.time()))

    @staticmethod
    def dateAdd(start_date_str, start_format_str='%Y-%m-%d %H:%M:%S', days=0, seconds=0,
                minutes=0, hours=0, weeks=0, end_format_str='%Y-%m-%d %H:%M:%S'):
        """
        返回指定格式时间字符串 偏移一段时间（n天前或n小时后） 之后的时间字符串
        :param start_date_str: 指定时间字符串
        :param format_str: 指定的时间字符串格式，默认为 %Y-%m-%d %H:%M:%S
        :param days: 偏移多少天
        :param seconds: 偏移多少秒
        :param minutes: 偏移多少分钟
        :param hours: 偏移多少小时
        :param weeks: 偏移多少星期
        :param end_format_str: 输出时间字符串的格式，默认为 %Y-%m-%d %H:%M:%S
        :return: 时间字符串，格式通过format_
        """
        start_date = datetime.datetime.strptime(start_date_str, start_format_str)
        days = datetime.timedelta(days=days, seconds=seconds, minutes=minutes, hours=hours, weeks=weeks)
        end_date = start_date + days
        return end_date.strftime(end_format_str)

    @staticmethod
    def str2datetime(string, format_str='%Y-%m-%d %H:%M:%S'):
        """
        将指定格式的时间字符串转化为 datetime类型
        :param string:  时间字符串
        :param format_str: 字符型， string参数的时间格式
        :return:  datatime类 实例对象
        """
        return datetime.datetime.strptime(string, format_str)

    @staticmethod
    def datetime2str(dt, format_str='%Y-%m-%d %H:%M:%S'):
        """
        将datetime类型数据转化为 指定格式的时间字符串
        :param date_:  datatime类 实例对象
        :param format_str: 字符型， string参数的时间格式
        :return:  整型时间戳
        """
        return dt.strftime(format_str)

    @staticmethod
    def stamp2datetime(stamp, timezone='UTC'):
        """
        将整型时间戳转为指定时区的datetime类型
        :param stamp: 整型时间戳
        :param timezone: 指定时区，UTC或CST
        :return:
        """
        # 判断时区参数是否是UTC或CST
        if timezone == 'UTC':
            # 创建一个UTC时区对象
            timezone = pytz.utc
        elif timezone == 'CST':
            # 创建一个北京时间（CST）时区对象
            timezone = pytz.timezone('Asia/Shanghai')
        else:
            # 抛出异常，提示无效的时区参数
            raise ValueError('Invalid timezone parameter. Must be UTC or CST.')
        # 将时间戳转换为带有时区的datetime对象
        dt = datetime.datetime.fromtimestamp(stamp, tz=timezone)
        # 返回datetime对象
        return dt

    @staticmethod
    def datetime2tamp(dt, timezone='UTC', replace=True):
        """
        将datetime类型转为指定时区的整型时间戳
        :param dt:  datetime类型
        :param timezone: 时区， UTC或CST
        :param replace:  转换还是替换时区，replace=True时，直接替换时区，即时间数只不变，转换时，表示转为另一时区同一时刻的时间（相差8小时）
        :return:
        """
        # 判断时区参数是否是UTC或CST
        if timezone == 'UTC':
            # 创建一个UTC时区对象
            timezone = pytz.utc
        elif timezone == 'CST':
            # 创建一个北京时间（CST）时区对象
            timezone = pytz.timezone('Asia/Shanghai')
        else:
            # 抛出异常，提示无效的时区参数
            raise ValueError('Invalid timezone parameter. Must be UTC or CST.')
        # 将datetime对象转换为带有时区的datetime对象
        if replace:
            dt = dt.replace(tzinfo=timezone)
        else:
            dt = dt.astimezone(timezone)
        # 将datetime对象转换为时间戳（秒）
        ts = datetime.datetime.timestamp(dt)
        # 四舍五入并转换为整数
        ts = int(round(ts))
        # 返回时间戳
        return ts

    @staticmethod
    def datebetween(string1, string2, format_str1='%Y-%m-%d %H:%M:%S', format_str2='%Y-%m-%d %H:%M:%S'):
        """
        求两个
        :param date_:  datatime类 实例对象
        :param format_str1: 字符型， string1参数的时间格式
        :param format_str2: 字符型， string2参数的时间格式
        :return:  整型时间戳
        """
        return datetime.datetime.strptime(string1, format_str1) - datetime.datetime.strptime(string2, format_str2)


def bar(obj, return_index=False, bar_len_total=50, bar_str='█', end='', step=1):
    """
    obj: 可迭代对象或整型数据，整型将转换为range(obj)
    return_index: 返回迭代元素的同时，是否返回索引
    bar_len_total: 进度条长度，默认为50
    bar_str: 进度条中的字符串，默认为'█'
    end_str: 完成全部进度后，需要打印的字符串
    step: 每个多少轮更新进度条
    """
    if isinstance(obj, int):
        obj = range(obj)
    assert isinstance(obj, Iterable), 'obj必须是整型或者可迭代对象'
    assert len(obj) > 0, '可迭代对象长度为0'
    obj_len = len(obj)
    start_time = time.time()
    now = obj[-1]
    for now, item in enumerate(obj, start=1):
        if return_index:
            yield now - 1, item
        else:
            yield item
        if now % step == 0:
            bar_len_now = bar_len_total * now // obj_len  # 当前轮次需要打印的bar_str个数
            end_time = time.time()
            print(
                f"\r{now / obj_len:<.0%}|{bar_str * bar_len_now:<{bar_len_total}}| {now}/{obj_len} [Time cost: {Timer.time_cost(start_time, end_time)}]",
                end='')
    print(
        f"\r{now / obj_len:<.0%}|{bar_str * bar_len_now:<{bar_len_total}}| {now}/{obj_len} [Time cost: {Timer.time_cost(start_time, end_time)}]",
        end='')
    print(end=end)


def bar2(now, total, need_print=True, bar_len_total=30, bar_str='█', info=None):
    """
    打印输出进度条
    now: 当前进度
    total: 需要迭代的总次数
    bar_len_total: 进度条长度，默认为50
    bar_str: 进度条中的字符串，默认为'█'
    info: 需要在进度条末尾打印的字符串
    """

    bar_len_now = bar_len_total * now // total  # 当前轮次需要打印的bar_str个数
    if info is None:
        string = f"{now / total:>8.2%}|{bar_str * bar_len_now:　<{bar_len_total}}| {now}/{total}"
    else:
        string = f"{now / total:>8.2%}|{bar_str * bar_len_now:　<{bar_len_total}}| {now}/{total}  {info}"
    if need_print:
        print(f"\r{string}",end='')
    else:
        return string


class GetFirstLetter(object):
    def is_contain_chinese(self, check_str):
        """
        判断字符串中是否包含中文
        :param check_str: {str} 需要检测的字符串
        :return: {bool} 包含返回True， 不包含返回False
        """
        for ch in check_str:
            if u'\u4e00' <= ch <= u'\u9fff':
                return True
        return False

    def single_get_first(self, string):
        """
        获取全拼的首字母
        """
        p = xpinyin.Pinyin()
        py = p.get_pinyin(string)
        return py[0]

    def getPinyin(self, string):
        """
        输出所有字的首字母
        """
        if string == None:
            return None
        string = string.replace('（', '(')
        s_list = string.split('(')
        s2_list = []
        for s in s_list:
            s = re.sub("[A-Za-z0-9\!\%\[\]\,\。（）()*-+=/]", "", s)
            lst = list(s)
            charLst = []
            for l in lst:
                charLst.append(self.single_get_first(l))
            s2_list.append(''.join(charLst))
        return '_'.join(s2_list)

class Cpen:
    """
    无论文件是否存在都写入文件，功能待完善
    """
    def __init__(self, path, mode, encoding='utf-8'):
        self.path = path
        self.mode = mode
        if not os.path.exists(path):
            with open(file=path, mode='w', encoding=encoding):
                pass
            self.f = open(file=path, mode=mode, encoding=encoding)
        else:
            self.f = open(file=path, mode=mode, encoding=encoding)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.f.close()

    def readline(self):
        while True:
            line = self.f.readline()
            if not line:
                break
            yield line

    def readlines(self, num_lines=100000):
        while True:
            lines = self.f.readlines(num_lines)
            if not lines:
                break
            yield lines


if __name__=='__main__':
    print(Timer.datebetween('2022-01-01 00:00:00', '2022-01-04 00:00:00'))
