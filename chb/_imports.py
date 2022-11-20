# -*- coding: utf-8 -*-
from ._importable import LazyImport, _get_import_statements

### Data Wrangling
pd = LazyImport("import pandas as pd")

np = LazyImport("import numpy as np")

dd = LazyImport("from dask import dataframe as dd")
SparkContext = LazyImport("from pyspark import SparkContext")

load_workbook = LazyImport("from openpyxl import load_workbook")

open_workbook = LazyImport("from xlrd import open_workbook")

wr = LazyImport("import awswrangler as wr")

### Data Visualization and Plotting
mpl = LazyImport("import matplotlib as mpl")
plt = LazyImport("import matplotlib.pyplot as plt")

sns = LazyImport("import seaborn as sns")

py = LazyImport("import plotly as py")
go = LazyImport("import plotly.graph_objs as go")
px = LazyImport("import plotly.express as px")

# dash = LazyImport("import dash")

# bokeh = LazyImport("import bokeh")

# alt = LazyImport("import altair as alt")

# pydot = LazyImport("import pydot")

### Image processing

cv2 = LazyImport("import cv2")
skimage = LazyImport("import skimage")
Image = LazyImport("from PIL import Image")
imutils = LazyImport("import imutils")

# statistics
statistics = LazyImport("import statistics")
stats = LazyImport("from scipy import stats")
sm = LazyImport("import statsmodels.api as sm")

# ### Time-Series Forecasting
# fbprophet = LazyImport("import fbprophet")
# Prophet = LazyImport("from fbprophet import Prophet")
# ARIMA = LazyImport("from statsmodels.tsa.arima_model import ARIMA")

### Machine Learning
sklearn = LazyImport("import sklearn")

LinearRegression = LazyImport("from sklearn.linear_model import LinearRegression")
LogisticRegression = LazyImport("from sklearn.linear_model import LogisticRegression")
Lasso = LazyImport("from sklearn.linear_model import Lasso")
LassoCV = LazyImport("from sklearn.linear_model import LassoCV")
Ridge = LazyImport("from sklearn.linear_model import Ridge")
RidgeCV = LazyImport("from sklearn.linear_model import RidgeCV")
ElasticNet = LazyImport("from sklearn.linear_model import ElasticNet")
ElasticNetCV = LazyImport("from sklearn.linear_model import ElasticNetCV")
PolynomialFeatures = LazyImport("from sklearn.preprocessing import PolynomialFeatures")
StandardScaler = LazyImport("from sklearn.preprocessing import StandardScaler")
MinMaxScaler = LazyImport("from sklearn.preprocessing import MinMaxScaler")
RobustScaler = LazyImport("from sklearn.preprocessing import RobustScaler")


OneHotEncoder = LazyImport("from sklearn.preprocessing import OneHotEncoder")
LabelEncoder = LazyImport("from sklearn.preprocessing import LabelEncoder")
TSNE = LazyImport("from sklearn.manifold import TSNE")
PCA = LazyImport("from sklearn.decomposition import PCA")
SimpleImputer = LazyImport("from sklearn.impute import SimpleImputer")
train_test_split = LazyImport("from sklearn.model_selection import train_test_split")
cross_val_score = LazyImport("from sklearn.model_selection import cross_val_score")
GridSearchCV = LazyImport("from sklearn.model_selection import GridSearchCV")
RandomizedSearchCV = LazyImport("from sklearn.model_selection import RandomizedSearchCV")
KFold = LazyImport("from sklearn.model_selection import KFold")
StratifiedKFold = LazyImport("from sklearn.model_selection import StratifiedKFold")

svm = LazyImport("from sklearn import svm")
GradientBoostingClassifier = LazyImport(
    "from sklearn.ensemble import GradientBoostingClassifier"
)
GradientBoostingRegressor = LazyImport(
    "from sklearn.ensemble import GradientBoostingRegressor"
)
RandomForestClassifier = LazyImport(
    "from sklearn.ensemble import RandomForestClassifier"
)
RandomForestRegressor = LazyImport("from sklearn.ensemble import RandomForestRegressor")

TfidfVectorizer = LazyImport(
    "from sklearn.feature_extraction.text import TfidfVectorizer"
)

CountVectorizer = LazyImport(
    "from sklearn.feature_extraction.text import CountVectorizer"
)

metrics = LazyImport("from sklearn import metrics")

sg = LazyImport("from scipy import signal as sg")

# Clustering
KMeans = LazyImport ("from sklearn.cluster import KMeans")

# Gradient Boosting Decision Tree
xgb = LazyImport("import xgboost as xgb")
lgb = LazyImport("import lightgbm as lgb")

# TODO: add all the other most important sklearn objects
# TODO: add separate sections within machine learning viz. Classification, Regression, Error Functions, Clustering

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
DataLoader = LazyImport("from torch.utils.data import DataLoader")
Dataset = LazyImport("from torch.utils.data import Dataset")
transforms = LazyImport("from torchvision import transforms")
trange = LazyImport("from tqdm import trange")

# NLP
nltk = LazyImport("import nltk")
gensim = LazyImport("import gensim")
spacy = LazyImport("import spacy")
re = LazyImport("import re")
textblob = LazyImport("import textblob")

# transformers
AutoModel = LazyImport("from transformers import AutoModel")
AutoTokenizer = LazyImport("from transformers import AutoTokenizer")
BertConfig = LazyImport("from transformers import BertConfig")

### Helper
os = LazyImport("import os")
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