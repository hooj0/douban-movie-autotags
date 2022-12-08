#!/usr/bin/env python3
# encoding: utf-8
# @author:   hoojo
# @email:    hoojo_@126.com
# @github:   https://github.com/hooj0
# @create:   2022/06/02
# @copyright by hoojo @2022
# @changelog Added douban movie autotags `log.py` python example


# ===============================================================================
# 标题：日志类，简单输出日志信息
# ===============================================================================
# 使用：利用 print 方法输出日志，枚举设置日志级别信息
# -------------------------------------------------------------------------------
# 描述：能输出不同级别的日志信息
# -------------------------------------------------------------------------------
from enum import Enum

from autotags import globals


# -------------------------------------------------------------------------------
# 构建日志级别枚举
# -------------------------------------------------------------------------------
class LogLevel(Enum):
    debug = 10
    info = 20
    warn = 30
    error = 40

    @staticmethod
    def of(name):
        for e in list(LogLevel):
            level = LogLevel(e)
            if level.name == name:
                return level
        return LogLevel.debug


# -------------------------------------------------------------------------------
# 构建日志类
# -------------------------------------------------------------------------------
class Log:

    def __init__(self, tag):
        self.__tag = tag
        self.__log_level = globals.LOG_LEVEL if globals.LOG_LEVEL is not None else LogLevel.debug

    def debug(self, message, *args):
        if self.__log_level.value <= 10:
            print(f"[DEBUG][{self.__tag}]", message, *args)

    def info(self, message, *args):
        if self.__log_level.value <= 20:
            print(f"[INFO][{self.__tag}]", message, *args)

    def warn(self, message, *args):
        if self.__log_level.value <= 30:
            print(f"[WARN][{self.__tag}]", message, *args)

    def error(self, message, *args):
        if self.__log_level.value <= 40:
            print(f"[ERROR][{self.__tag}]", message, *args)
