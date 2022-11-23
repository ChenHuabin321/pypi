# -*- coding: utf-8 -*-
from ._importable import LazyImport, _get_import_statements

pd = LazyImport("import pandas as pd")
np = LazyImport("import numpy as np")

os = LazyImport("import os")
re = LazyImport("import re")
time = LazyImport("import time")
sys = LazyImport("import sys")
random = LazyImport("import random")
glob = LazyImport("import glob")
logging = LazyImport("import logging")
Path = LazyImport("from pathlib import Path")
pickle = LazyImport("import pickle")
json = LazyImport("import json")

dt = LazyImport("import datetime as dt")
datetime = LazyImport("import datetime")

tqdm = LazyImport("import tqdm")
trange = LazyImport("from tqdm import trange")


redis = LazyImport("import redis")
cx_Oracle = LazyImport("import cx_Oracle")
pymongo = LazyImport("import pymongo")
pymysql = LazyImport("import pymysql")

threading = LazyImport("import threading")
Thread = LazyImport("from threading import Thread")
Process = LazyImport("from multiprocessing import Process")
multiprocessing = LazyImport("import multiprocessing import Process")
queue = LazyImport("import queue")

MongoDao = LazyImport("from chb._dao import MongoDao")
OracleDao = LazyImport("from chb._dao import OracleDao")
MysqlDao = LazyImport("from chb._dao import MysqlDao")
RedisDao = LazyImport("from chb._dao import RedisDao")
Log = LazyImport("from chb._log import Log")
get_current_path = LazyImport("from chb._utils import get_current_path")
get_time_str = LazyImport("from chb._utils import get_time_str")
MutilThreadReader = LazyImport("from chb._utils import MutilThreadReader")
Tableprint = LazyImport("from chb._utils import Tableprint")

def all_import():
    """所有导入语句"""
    return _get_import_statements(globals(), was_imported=None)

def unimport():
    """所有未执行导入的语句"""
    return _get_import_statements(globals(), was_imported=False)

def imported(print_statements=True):
    """所有已经执行导入的语句"""
    statements = _get_import_statements(globals(), was_imported=True)
    if print_statements:
        print("\n".join(statements))
    return statements