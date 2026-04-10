# 导包
import logging.handlers
import os
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
# 定义日志文件路径
LOG_PATH = os.path.join(BASE_DIR, "log")
if not os.path.exists(LOG_PATH):
    os.mkdir(LOG_PATH)


class GetLogger:
    logger222 = None

    @classmethod
    def get_logger(cls):
        cls.logname = os.path.join(LOG_PATH, "{}.log".format(time.strftime("%Y%m%d")))
        if cls.logger222 is None:
            # 获取logger对象,name="admin",表示日志器所有者名
            cls.logger222 = logging.getLogger("admin")

            # 设置日志器日志级别，其添加的所有处理器都受影响
            cls.logger222.setLevel(logging.DEBUG)
            # 避免重复添加处理器
            cls.logger222.handlers.clear()

            # 获取控制台handler对象
            sh = logging.StreamHandler()
            sh.setLevel(logging.INFO)  # 控制台输出 INFO 及以上级别

            # 获取文件handler（时间分割）对象
            th = logging.handlers.TimedRotatingFileHandler(filename=cls.logname,when="h", interval=2,
                                                          backupCount=3, encoding='utf-8')

            #设置文件日志级别 - 记录所有 DEBUG 及以上级别的日志
            th.setLevel(logging.DEBUG)

            # 设置formatter
            fmt = "%(asctime)s  %(levelname)s [%(name)s] [%(filename)s(%(funcName)s:%(lineno)d)] -%(message)s"
            fm = logging.Formatter(fmt)

            # 为处理器handler对象添加格式器
            sh.setFormatter(fm)
            th.setFormatter(fm)

            # 为logger对象添加处理器
            cls.logger222.addHandler(sh)
            cls.logger222.addHandler(th)
        return cls.logger222

