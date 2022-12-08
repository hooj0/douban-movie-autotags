#!/usr/bin/env python3
# encoding: utf-8
# @author:   hoojo
# @email:    hoojo_@126.com
# @github:   https://github.com/hooj0
# @create:   2022/06/02
# @copyright by hoojo @2022
# @changelog Added douban movie autotags `utils.py` python example


# ===============================================================================
# 标题：工具类
# ===============================================================================
# 使用：工具类，提供常用工具方法
# -------------------------------------------------------------------------------
# 描述：提供常用工具方法
# -------------------------------------------------------------------------------
from autotags.log import Log


# -------------------------------------------------------------------------------
# 构建系统工具类
# -------------------------------------------------------------------------------
class Utils:
    __log = Log("Utils")

    @classmethod
    def get(cls, data, key, default_value):
        value = data.get(key, default_value)
        value = default_value if value is None else value
        cls.__log.debug("dict.get('%s') = %s" % (key, value))
        return value