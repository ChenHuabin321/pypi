# -*- coding: utf-8 -*-
from chb.utils import Tableprint

t = Tableprint(['a', '中国人', '1256546547654765'],pad_len=10)
t.print_header()
t.print_row(123,456,798)