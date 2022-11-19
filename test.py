# -*- coding: utf-8 -*-
from chb.utils import Tableprint

t = Tableprint(['第一列', '第二列', '第三列'], align='<', pad_len=10)
t.print_header()
t.print_row(123,456,798)