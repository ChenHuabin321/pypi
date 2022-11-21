# -*- coding: utf-8 -*-
import os
import logging


class Log():
    """
    日志类，记录运行状态
    """
    def __init__(self, logger_name=None, file_handler=False, log_dir='.'):
        self.logger_name = logger_name
        if logger_name:
            self.logger = logging.getLogger(logger_name)
        else:
            self.logger = logging.getLogger('chb')
        self.logger.setLevel(level=logging.DEBUG)

        # Formatter
        file_logging_format = logging.Formatter(
            fmt='%(asctime)s , %(name)s , %(process)d, %(levelname)s , %(filename)s %(funcName)s  line %(lineno)s ,'
                ' %(message)s',
            datefmt='%Y-%m-%d  %H:%M:%S %a')
        stream_logging_format = logging.Formatter(fmt='%(asctime)s %(funcName)s line %(lineno)s'' out: %(message)s',
                                           datefmt='%Y-%m-%d %H:%M:%S')


        # StreamHandler
        if len(self.logger.handlers) == 0:  # 如果没有添加过日志器，则添加（避免多次创建日志器造成日志重复输出多行）
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(stream_logging_format)
            self.logger.addHandler(stream_handler)
        # FileHandler

        if file_handler:
            if len(self.logger.handlers) <= 1:  # 如果小于等于1个日志器，表明没有添加过文件日志器
                if self.logger_name:
                    log_file = os.path.join(log_dir, self.logger_name, '.log')
                else:
                    log_file = os.path.join(log_dir, 'chb.log')
                file_handler = logging.FileHandler(log_file, encoding='UTF-8')
                file_handler.setFormatter(file_logging_format)
                self.logger.addHandler(file_handler)

    def __call__(self, level='info'):
        """
        如果level为None，则返回日志器，否则返回对应等级的输出函数：debug、info等
        :param level:
        :return:
        """
        if level:
            return getattr(self.logger, level)
        else:
            return self.logger

    def getLogger(self, level='info'):
        """
        如果level为None，则返回日志器，否则返回对应等级的输出函数：debug、info等
        :param level:
        :return:
        """
        return self.__call__(level)

