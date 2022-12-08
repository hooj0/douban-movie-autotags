#!/usr/bin/env python3
# encoding: utf-8
# @author:   hoojo
# @email:    hoojo_@126.com
# @github:   https://github.com/hooj0
# @create:   2022/06/02
# @copyright by hoojo @2022
# @changelog Added douban movie autotags `const.py` python example


# ===============================================================================
# 标题：构建常量，不能重复且必须大写
# ===============================================================================
# 使用：利用 __setattr__ 方法构建常量，利用 self.__dict__[name] = value 设置常量值
# -------------------------------------------------------------------------------
# 描述：利用 __setattr__ 方法构建常量，检查常量名称，且不能重复声明
# -------------------------------------------------------------------------------
import sys
from autotags.log import Log


# -------------------------------------------------------------------------------
# 构建自定义常量类
# -------------------------------------------------------------------------------
class __Const:

    __log = Log("Const")

    # 自定义异常处理
    class ConstError(PermissionError):
        pass

    class ConstCaseError(ConstError):
        pass

    # 重写 __setattr__() 方法
    def __setattr__(self, name, value):
        # 已包含该常量，不能二次赋值，None 除外
        if name in self.__dict__ and self.__dict__.get(name) is not None:
            raise self.ConstError(f"Const '{name}' value cannot be modified.")

        # 所有的字母需要大写
        if not name.isupper():
            raise self.ConstCaseError(f"Const name '{name}' is not all uppercase")
        self.__dict__[name] = value

    def to_string(self):
        self.__log.debug(f"const string of {self.__dict__}")


_ = __Const()
sys.modules[__name__] = _

_.USER_DATA_DIR = ".user-cache"
_.BROWSER_BACKGROUND = False
_.TIMEOUT = 600

_.USER = "hoojo"
_.TAGS = "N"

_.to_string()
