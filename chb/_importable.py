# -*- coding: utf-8 -*-

# 注：此部分代码修改自pyforest


class LazyImport(object):
    def __init__(self, import_statement):
        self.__import_statement__ = import_statement
        # the next line does not work for general imports, e.g. "from pandas import *"
        self.__imported_name__ = import_statement.strip().split()[-1]

        # self.__complementary_imports__ = []
        self.__was_imported__ = False
        self.__doc__ = '注意：执行调用、dir、getattr等方法后才能查看__doc__'
        self.__signature__ = '注意：执行调用、dir、getattr等方法后才能查看__signature__'

    def __maybe_import__(self):
        """
        真实执行导入的方法函数
        """
        # self.__maybe_import_complementary_imports__()
        if not self.__was_imported__:
            exec(self.__import_statement__, globals())   # 执行导入
            self.__was_imported__ = True  # 将是否已导入改为True
            self.__maybe_add_docstring_and_signature__()

    def __maybe_add_docstring_and_signature__(self):
        """
        将__doc__和__signature__赋值给惰性导入对象，注意，这两个对象只能在调用__maybe_import__内部调用才能生效。
        """
        try:
            self.__doc__ = eval(f"{self.__imported_name__}.__doc__")

            from inspect import signature

            self.__signature__ = eval(f"signature({self.__imported_name__})")
        except:
            pass

    def __dir__(self):
        self.__maybe_import__()
        return eval(f"dir({self.__imported_name__})")

    def __getattr__(self, attribute):
        self.__maybe_import__()
        return eval(f"{self.__imported_name__}.{attribute}")

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
            return f"active chb.LazyImport of {eval(self.__imported_name__)}"
        else:
            return f"lazy chb.LazyImport for '{self.__import_statement__}'"


def _get_import_statements(symbol_dict, was_imported):
    statements = []
    for _, symbol in symbol_dict.items():
        if isinstance(symbol, LazyImport):
            if was_imported:
                if symbol.__was_imported__:
                    statements.append(symbol.__import_statement__)
            elif was_imported is None:
                statements.append(symbol.__import_statement__)
            else:
                if not symbol.__was_imported__:
                    statements.append(symbol.__import_statement__)
    statements = list(set(statements))
    return statements

