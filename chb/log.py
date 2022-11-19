# -*- coding: utf-8 -*-
import os
import logging


class Log():
    """
    日志类，记录运行状态
    """

    def __init__(self, logger_name=__name__, file_handler=False, log_dir='.'):
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(level=logging.DEBUG)

        # Formatter
        logging_format = logging.Formatter(
            fmt='%(asctime)s , %(name)s , %(process)d, %(levelname)s , %(filename)s %(funcName)s  line %(lineno)s ,'
                ' %(message)s',
            datefmt='%Y-%m-%d  %H:%M:%S %a')
        #
        #
        # timefilehandler = logging.handlers.TimedRotatingFileHandler(log_file, when='D', interval=45,
        #                                                             backupCount=1)
        # # 设置后缀名称，跟strftime的格式一样
        # timefilehandler.suffix = "%Y-%m-%d.log"
        # timefilehandler.setFormatter(logging_format)
        # self.logger.addHandler(timefilehandler)

        # # FileHandler
        if file_handler:
            log_file = os.path.join(log_dir, logger_name + '.log')
            file_handler = logging.FileHandler(log_file, encoding='UTF-8')
            file_handler.setFormatter(logging_format)
            self.logger.addHandler(file_handler)

        # # StreamHandler
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(logging_format)
        self.logger.addHandler(stream_handler)

    def getLogger(self, level='info'):
        return getattr(self.logger, level)
