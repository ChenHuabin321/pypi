# -*- coding: utf-8 -*-
"""
本模块主要提供以下功能：
1. 提供Python常用工具库的惰性导入
2. 常用数据库（MySQL、Oracle、MongoDB、Redis）的with连接功能
3. 对Python中logging进行封装，方便记录日志
4. 提供增量打印表格、获取当前路径字符串、当前时间字符串、单线程转多线程读取文件装饰器等常用函数方法

详细说明如下：
1. 惰性导入
使用该功能时，建议在代码文件首行运行下行代码：
from chb import *
这行代码会惰性导入Python中常用的近百个工具库，请参考文件最下方列表。这些工具库只是以惰性导入的方式存在，只在代码中进行使用（查看文档除外）时才会真实导入
所以，无需担心会导入上百个工具库导致占用内存和命名空间混乱。例如下方代码：

from chb import *
time.sleep(2)

在执行`time.sleep(2)`前，time只是一个占位符，并不是真实的time内置模块，在执行这行代码后，原来的占"位变量"time会被覆盖，变为真实的time内置模块。
注意，对time进行print、获取time的属性、调用time内的方法，都会执行真实导入。但time.__doc__在真实导入前并不会返回真实time模块的文档。

2. with上下文数据库连接功能。MySQL、Oracle、MongoDB、RedisDao的上下文连接类名如下：
(1) MysqlDao
(2) OracleDao
(3) MongoDao
(4) RedisDao
请知悉，这些类也是以惰性方式导入，可以直接使用，并不需要再次执行import。另外，这些类也依赖于对应的第三方工具包，例如MysqlDao依赖于pymysql，请在使用前先安装对应依赖包。

3. 日志器封装
对Python中logging模块进行封装，获得Log类，可以通过以下代码示例使用：

from chb import *

log = Log().getLogger('info')
# log = Log()()  # 与上行等效

log(123)

输出效果如下：
2022-11-21 21:02:41 <module> line 1 out: 123

如果你愿意的话，可以额外安装工具库 colorlog ，上行输出结果将有更加不错的视觉效果。当然，colorlog不是必须的。

4. 其他工具方法
（1）增量打印表格。使用示例如下：
from chb import *
t = Tableprint(headers=['epoch', 'loss', 'acc'])
t.print_header()
for epoch in range(3):
    t.print_row(epoch, 0.5, 0.5)
每一轮for循环将打印一行，输出效果如下：
+======+===========+==========+=========+
|      |   epoch   |   loss   |   acc   |
+======+===========+==========+=========+
|  1   |     0     |   0.5    |   0.5   |
+------+-----------+----------+---------+
|  2   |     1     |   0.5    |   0.5   |
+------+-----------+----------+---------+
|  3   |     2     |   0.5    |   0.5   |
+------+-----------+----------+---------+

(2) 获取当前绝对路径字符串

from chb import *
path = get_current_path()
print(path)

输出结果如下：
/data/chb/jupyter

(3) 当前时间字符串

from chb import *
path = get_time_str()
print(path)

输出结果如下：
20221121211534

可以给get_time_str传递格式参数：get_time_str(format='%Y%m%d%H%M%S')

(4) 单线程转多线程读取文件
写好读取单个文件的方法函数后，用MutilThreadReader进行装饰，同时传递需要读取的文件路径列表。如下所示：

@MutilThreadReader(['./data/excel文件1.xlsx', './data/excel文件2.xlsx', './data/excel文件3.xlsx'], 3)
def read_excel(path):
    pass
"""
from ._imports import *  # 惰性导入N多模块
