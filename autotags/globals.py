#!/usr/bin/env python3
# encoding: utf-8
# @author:   hoojo
# @email:    hoojo_@126.com
# @github:   https://github.com/hooj0
# @create:   2022/6/14 0014
# @copyright by hoojo @2022
# @changelog Added douban movie autotags `globals` python example


# ===============================================================================
# 标题：构建全局变量
# ===============================================================================
# 使用：构建全局变量类，用于存储全局变量数据，支持跨文件操作
# -------------------------------------------------------------------------------
# 描述：用于存储全局变量数据，支持跨文件操作
# -------------------------------------------------------------------------------
import sys


# -------------------------------------------------------------------------------
# 构建全局变量类
# -------------------------------------------------------------------------------
class __Globals:
    # 自定义异常处理
    class GlobalsError(PermissionError):
        pass

    class GlobalsCaseError(GlobalsError):
        pass

    # 重写 __setattr__() 方法
    def __setattr__(self, name, value):
        if name in self.__dict__ and self.__dict__.get(name) is not None:
            raise self.GlobalsError(f"Globals variable '{name}' value cannot not None.")

        # 所有的字母需要大写
        if not name.isupper():
            raise self.GlobalsCaseError(f"Global variable name '{name}' is not all uppercase")

        if name in self.__dict__:
            print(f"[TOP] Global variable '{name}' value is modified '{self.__dict__[name]}' to '{value}'")
        self.__dict__[name] = value

        _.to_string()

    def to_string(self):
        print(f"[TOP] Global string of {self.__dict__}")


_ = __Globals()
sys.modules[__name__] = _

_.LOG_LEVEL = None
