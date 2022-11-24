# -*- coding: utf-8 -*-
from ._importable import LazyImport, _get_import_statements

### Data Wrangling
pd = LazyImport("import pandas as pd")
np = LazyImport("import numpy as np")

### Data Visualization and Plotting
mpl = LazyImport("import matplotlib as mpl")
plt = LazyImport("import matplotlib.pyplot as plt")
sns = LazyImport("import seaborn as sns")
Image = LazyImport("from PIL import Image")


xgb = LazyImport("import xgboost as xgb")
lgb = LazyImport("import lightgbm as lgb")

# Deep Learning
tf = LazyImport("import tensorflow as tf")
keras = LazyImport("import keras")
torch = LazyImport("import torch")
fastai = LazyImport("import fastai")
nn = LazyImport("import torch.nn as nn")
F = LazyImport("import torch.nn.functional as F")
optim = LazyImport("import torch.optim as optim")
lr_scheduler = LazyImport("from torch.optim import lr_scheduler")
cudnn = LazyImport("import torch.backends.cudnn as cudnn")
torchvision = LazyImport("import torchvision")
datasets = LazyImport("from torchvision import datasets")
models = LazyImport("from torchvision import models")
Conv2d = LazyImport("from torch.nn import Conv2d")
MaxPool2d = LazyImport("from torch.nn import MaxPool2d")
Flatten = LazyImport("from torch.nn import Flatten")
Linear = LazyImport("from torch.nn import Linear")
Sequential = LazyImport("from torch.nn import Sequential")
dataloader = LazyImport("from torch.utils.data import dataloader")
DataLoader = LazyImport("from torch.utils.data.dataloader import DataLoader")
dataset = LazyImport("from torch.utils.data import dataset")
Dataset = LazyImport("from torch.utils.data.dataset import Dataset")
transforms = LazyImport("from torchvision import transforms")
trange = LazyImport("from tqdm import trange")
tqdm = LazyImport("from tqdm import tqdm")

# NLP
nltk = LazyImport("import nltk")
gensim = LazyImport("import gensim")
spacy = LazyImport("import spacy")

textblob = LazyImport("import textblob")

# transformers
AutoModel = LazyImport("from transformers import AutoModel")
AutoTokenizer = LazyImport("from transformers import AutoTokenizer")
BertConfig = LazyImport("from transformers import BertConfig")

### Helper
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


## database
redis = LazyImport("import redis")
cx_Oracle = LazyImport("import cx_Oracle")
pymongo = LazyImport("import pymongo")
pymysql = LazyImport("import pymysql")

## 并发
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

set_device = LazyImport("from chb._utils import set_device")
get_current_path = LazyImport("from chb._utils import get_current_path")
get_time_str = LazyImport("from chb._utils import get_time_str")
MutilThreadReader = LazyImport("from chb._utils import MutilThreadReader")
Tableprint = LazyImport("from chb._utils import Tableprint")

def all_import(print_statements=True):
    """所有导入语句"""
    statements = sorted(_get_import_statements(globals(), was_imported=None))
    if print_statements:
        print("\n".join(statements))
    return statements

def unimport(print_statements=True):
    """所有未执行导入的语句"""
    statements = sorted(_get_import_statements(globals(), was_imported=False))
    if print_statements:
        print("\n".join(statements))
    return statements

def imported(print_statements=True):
    """所有已经执行导入的语句"""
    statements = _get_import_statements(globals(), was_imported=True)
    if print_statements:
        print("\n".join(statements))
    return statements