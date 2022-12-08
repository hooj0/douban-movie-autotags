#!/usr/bin/env python3
# encoding: utf-8
# @author:   hoojo
# @email:    hoojo_@126.com
# @github:   https://github.com/hooj0
# @create:   2022/06/02
# @copyright by hoojo @2022
# @changelog Added douban movie autotags `setup.py` python example


# ===============================================================================
# 标题：douban movie 自动打标签工具
# ===============================================================================
# 使用：利用 playwright 在浏览器中执行脚本
# -------------------------------------------------------------------------------
# 描述：启动程序
# -------------------------------------------------------------------------------
import getopt
import os
import sys
from autotags.core import Core


# -------------------------------------------------------------------------------
# 构建单例运行脚本程序
# -------------------------------------------------------------------------------
def main(argv):
    print('argv: %s' % argv)

    Core().run()


if __name__ == "__main__":
    main(sys.argv[1:])