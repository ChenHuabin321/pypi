# -*- coding: utf-8 -*-
# 注：此部分代码修改自pyforest
class LazyImport(object):
    def __init__(self, import_statement):
        self.__import_statement__ = import_statement
        # the next line does not work for general imports, e.g. "from pandas import *"
        self.__imported_name__ = import_statement.strip().split()[-1]

        self.__complementary_imports__ = []
        self.__was_imported__ = False

    def __on_import__(self, lazy_import):
        self.__complementary_imports__.append(lazy_import)

    def __maybe_import_complementary_imports__(self):
        for lazy_import in self.__complementary_imports__:
            try:
                lazy_import.__maybe_import__()
            except:
                # silently fails if the complementary lazy_import is not available.
                # This is because complementary lazy_imports are considered optional.
                # Please note that direct imports of lazy_imports will fail explicitly.
                pass

    # Python will only import the module(s) if they are missing
    # if the module(s) were imported before, this method returns immediately
    def __maybe_import__(self):
        self.__maybe_import_complementary_imports__()
        exec(self.__import_statement__, globals())
        # Attention: if the import fails, the next lines will not be reached
        self.__was_imported__ = True
        self.__maybe_add_docstring_and_signature__()

        # Always update the import cell again
        # this is not problem because the update is fast
        # but it solves the problem of updating the first cell even if the first import was triggered via autocomplete
        # when the import cell is only updated the first time, autocompletes wont result in updated cells
        # Attention: the first cell is not updated after the autocomplete but after the cell (with the autocomplete) is executed
        _update_import_cell()

    def __maybe_add_docstring_and_signature__(self):
        # adds docstrings for imported objects
        # UnitRegistry = LazyImport("from pint import UnitRegistry")
        # UnitRegistry?

        try:
            self.__doc__ = eval(f"{self.__imported_name__}.__doc__")

            from inspect import signature

            self.__signature__ = eval(f"signature({self.__imported_name__})")
        except:
            pass

    # among others, called during auto-completion of IPython/Jupyter
    def __dir__(self):
        self.__maybe_import__()
        return eval(f"dir({self.__imported_name__})")

    # called for undefined attribute and returns the attribute of the imported module
    def __getattr__(self, attribute):
        self.__maybe_import__()
        return eval(f"{self.__imported_name__}.{attribute}")

    # called for callable objects, e.g. from pathlib import Path; Path(".")
    def __call__(self, *args, **kwargs):
        self.__maybe_import__()
        return eval(self.__imported_name__)(*args, **kwargs)

    def __repr__(self, *args, **kwargs):
        # it is important that __repr__ does not trigger an import if the lazy_import is not yet imported
        # e.g. if the user calls locals(), this triggers __repr__ for each object
        # and this would result in an import if the lazy_import is not yet imported
        # and those imports might fail explicitly if the lazy_import is not available
        # and this would break locals() for the user

        if self.__was_imported__:
            # next line only adds imported_name into the local scope but does not trigger a new import
            # because the lazy_import was already imported via another trigger
            self.__maybe_import__()
            return f"active pyforest.LazyImport of {eval(self.__imported_name__)}"
        else:
            return f"lazy pyforest.LazyImport for '{self.__import_statement__}'"


def _update_import_cell():
    try:
        from IPython.display import display, Javascript
    except ImportError:
        return

    # import here and not at top of file in order to not interfere with importables
    from ._imports import active_imports

    statements = active_imports(print_statements=False)

    display(
        Javascript(
            """
        if (window._pyforest_update_imports_cell) {{ window._pyforest_update_imports_cell({!r}); }}
    """.format(
                "\n".join(statements)
            )
        )
    )


def _get_import_statements(symbol_dict, was_imported=True):
    statements = []
    for _, symbol in symbol_dict.items():
        if isinstance(symbol, LazyImport) and (symbol.__was_imported__ == was_imported):
            statements.append(symbol.__import_statement__)

    # remove potential duplicates, e.g. when user_symbols are passed
    statements = list(set(statements))
    return statements


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

dash = LazyImport("import dash")

bokeh = LazyImport("import bokeh")

alt = LazyImport("import altair as alt")

pydot = LazyImport("import pydot")

### Image processing

cv2 = LazyImport("import cv2")
skimage = LazyImport("import skimage")
Image = LazyImport("from PIL import Image")
imutils = LazyImport("import imutils")

# statistics
statistics = LazyImport("import statistics")
stats = LazyImport("from scipy import stats")
sm = LazyImport("import statsmodels.api as sm")

### Time-Series Forecasting
fbprophet = LazyImport("import fbprophet")
Prophet = LazyImport("from fbprophet import Prophet")
ARIMA = LazyImport("from statsmodels.tsa.arima_model import ARIMA")

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
sys = LazyImport("import sys")
os = LazyImport("import os")
random = LazyImport("import random")
time = LazyImport("import time")
glob = LazyImport("import glob")
Path = LazyImport("from pathlib import Path")

pickle = LazyImport("import pickle")

dt = LazyImport("import datetime as dt")

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


##################################################
### dont make adjustments below this line ########
##################################################


#############################
### User-specific imports ###
#############################
# You can save your own imports in ~/.pyforest/user_imports.py
# Please note: imports in ~/.pyforest/user_imports.py take precedence over the
# imports above.

# _load_user_specific_imports(globals())
# # don't want to blow up the namespace
# del _load_user_specific_imports


# #######################################
# ### Complementary, optional imports ###
# #######################################
# # Why is this needed? Some libraries patch existing libraries
# # Please note: these imports are only executed if you already have the library installed
# # If you want to deactivate specific complementary imports, do the following:
# # - uncomment the lines which contain `.__on_import__` and the library you want to deactivate

# pandas_profiling = LazyImport("import pandas_profiling")
# pd.__on_import__(pandas_profiling)  # adds df.profile_report attribute to pd.DataFrame

# bam = LazyImport("import bamboolib as bam")
# pd.__on_import__(bam)  # adds GUI to pd.DataFrame when IPython frontend can display it


def lazy_imports():
    return _get_import_statements(globals(), was_imported=False)


def active_imports(print_statements=True):
    statements = _get_import_statements(globals(), was_imported=True)
    if print_statements:
        print("\n".join(statements))
    return statements
