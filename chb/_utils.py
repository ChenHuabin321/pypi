# -*- coding: utf-8 -*-
from ._imports import *
import queue
import torch
from threading import Thread
from chb._log import Log
log = Log(message_only=True)()

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

def time_cost(start_time, end_time):
    """
    自适应输出时间消耗
    start_time：开始时间
    end_time：结束时间
    示例：time_cost(0, 3668)  # 返回： 1h 1m 8s
    """
    cost = end_time - start_time
    h = f"{int(cost // 3600):d} h " if cost // 3600 else ""
    m = f"{int(cost % 3600 // 60):d} m " if cost % 3600 // 60 else ""
    s = f"{round(cost % 3600 % 60, 5)} s" if cost % 3600 % 60 else ""
    return f"{h}{m}{s}"

def bar(obj, return_index=False, bar_len_total=50, bar_str='█', end='', step=1):
    """
    obj: 可迭代对象或整型数据，整型将转换为range(obj)
    return_index: 返回迭代元素的同时，是否返回索引
    bar_len_total: 进度条长度，默认为50
    bar_str: 进度条中的字符串，默认为'█'
    end_str: 完成全部进度后，需要打印的字符串
    step: 每个多少轮更新进度条
    """
    from collections.abc import Iterable
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
                f"\r{now / obj_len:<.0%}|{bar_str * bar_len_now:<{bar_len_total}}| {now}/{obj_len} [Time cost: {time_cost(start_time, end_time)}]",
                end='')
    print(
        f"\r{now / obj_len:<.0%}|{bar_str * bar_len_now:<{bar_len_total}}| {now}/{obj_len} [Time cost: {time_cost(start_time, end_time)}]",
        end='')
    print(end=end)


def bar2(now, total, bar_len_total=50, bar_str='█', info=None):
    """
    now: 当前进度
    total: 需要迭代的总次数
    bar_len_total: 进度条长度，默认为50
    bar_str: 进度条中的字符串，默认为'█'
    info: 需要在进度条末尾打印的字符串
    """

    bar_len_now = bar_len_total * now // total  # 当前轮次需要打印的bar_str个数
    if info is None:
        print(
            f"\r{now / total:<.0%}|{bar_str * bar_len_now:<{bar_len_total}}| {now}/{total}",
            end='')
    else:
        print(
            f"\r{now / total:<.0%}|{bar_str * bar_len_now:<{bar_len_total}}| {now}/{total}  {info}",
            end='')


class Timer:
    """
    计时器，统计一段代码的运行时长
    使用方法：
    with Timer():
        pass
    """
    def __init__(self):
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        info = time_cost(self.start_time, time.time())
        log(f'Time Cost: {info}')
