#!/usr/bin/env python3
# encoding: utf-8
# @author:   hoojo
# @email:    hoojo_@126.com
# @github:   https://github.com/hooj0
# @create:   2022/7/6 0015
# @copyright by hoojo @2022
# @changelog Added douban movie autotags `playwright runner` python example


# ===============================================================================
# 标题：核心业务处理
# ===============================================================================
# 使用：利用 playwright 在浏览器中执行 JavaScript 代码
# -------------------------------------------------------------------------------
# 描述：将打包 JavaScript 代码放入到 https://hamibot.cn/dashboard/scripts/ 运行
# -------------------------------------------------------------------------------
import asyncio
import random
import sys
import time
import os

from playwright.async_api import async_playwright
from autotags import const
from autotags import log


# -------------------------------------------------------------------------------
# 构建编辑器对象
# -------------------------------------------------------------------------------
class Core:

    def __init__(self):

        self.name = type(self).__name__
        self.log = log.Log(self.name)

    def run(self):
        # 获取事件循环
        if os.name == 'nt':
            loop = asyncio.ProactorEventLoop()
            asyncio.set_event_loop(loop)
        else:
            loop = asyncio.get_event_loop()

        loop.run_until_complete(self.__run_browser())

    # noinspection PyMethodMayBeStatic
    def __screen_size(self):
        """
        使用tkinter获取屏幕大小
        """
        import tkinter
        tk = tkinter.Tk()

        width = tk.winfo_screenwidth()
        height = tk.winfo_screenheight()

        tk.quit()

        return width, height

    def __find_tag(self, text_list, prefix):
        for tag in text_list:
            if tag.startswith(prefix):
                return tag.replace(prefix, '')
        return None

    def __parse_tag(self, text_list, prefix, index):
        text = self.__find_tag(text_list, prefix)

        if text is None:
            self.log.error("Could not find tag: ", prefix)
            return None

        if text.count("/") > 0:
            return text.split("/")[index].strip()
        else:
            return text.strip()

    async def __changed_tag(self, page):
        info_el = page.locator("div.article div#info")
        info_contents = (await info_el.inner_text()).split("\n")

        tags_name = const.TAGS
        category = self.__parse_tag(info_contents, "类型: ", 1)
        country = self.__parse_tag(info_contents, "制片国家/地区: ", 0)
        tag_text = tags_name + " " + category + " " + country
        self.log.debug("movie detail: ", info_contents)
        self.log.debug("movie type: ", category)
        self.log.debug("movie country: ", country)
        self.log.debug("movie tag: ", tag_text)

        await page.locator("div.article a:has-text('修改')").click()
        await page.wait_for_selector("div#dialog")

        dialog_el = page.locator("div#dialog")
        await dialog_el.locator("input[name=tags]").fill(tag_text)

        await dialog_el.locator("input:has-text('保存') >> visible=true").click()
        await page.wait_for_selector("div#dialog", timeout=0, state="visible")

        # await asyncio.sleep(random.randrange(1, 3))

    async def __open_movie(self, page, movie_el):
        tags_name = const.TAGS
        tagged_count = await movie_el.locator("span.tags:text('%s')" % tags_name).count()
        print("tagged: %s" % tagged_count)
        title = await movie_el.locator("li.title a").inner_text()
        if tagged_count != 1:
            self.log.debug("open movie:", title)
            # await asyncio.sleep(random.randrange(1, 3))

            await movie_el.locator("li.title a").click()
            await page.wait_for_selector("div#info", timeout=0)
            self.log.debug("movie detail load success")

            await self.__changed_tag(page)
            await page.go_back()
        else:
            self.log.debug("tagged movie:", title)

    async def __movie_list(self, page):
        # 设置请求URL
        url = f"https://movie.douban.com/people/{const.USER}/wish"

        # 地址栏跳转到当前网址
        response = await page.goto(url, timeout=0)
        self.log.debug("request url:", url)
        self.log.debug("response url:", response.url)
        self.log.info("open page: %s, ok: %s" % (await page.title(), response.ok))

        await page.wait_for_selector("div.article", timeout=0)
        await page.wait_for_load_state()
        self.log.debug("console load success")

        tags_name = const.TAGS
        tagged_el = page.locator("div.grid-view div.item", has=page.locator("span.tags:text('%s')" % tags_name))
        tagged_el_count = await tagged_el.count()
        if tagged_el_count >= 15:
            self.log.error("No movies were found to be labeled `%s`." % tags_name)
            exit("No movies were found to be labeled `%s`." % tags_name)
        else:
            self.log.info("Movies were found to be labeled `%s`." % tagged_el_count)

        movie_els = page.locator("div.grid-view div.item")
        movie_els_count = await movie_els.count()
        print("Found movies count: %d" % movie_els_count)

        for i in range(movie_els_count):
            movie_el = movie_els.nth(i)

            await self.__open_movie(page, movie_el)

    async def __run_browser(self):
        self.log.info("start the browser to run the script")
        # 运行时变量参数
        timeout, headless, data_dir = const.TIMEOUT, const.BROWSER_BACKGROUND, const.USER_DATA_DIR
        # 获取屏幕尺寸
        width, height = self.__screen_size()

        async with async_playwright() as playwright:
            # 启动浏览器
            context = await playwright.chromium.launch_persistent_context(data_dir, headless=headless, devtools=False,
                                                                          timeout=(1000 * timeout), java_script_enabled=True, no_viewport=True, locale="zh-CN",
                                                                          user_agent="Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36",
                                                                          args=["--disable-infobars", "--start-maximized"])
            # 获取所有打开的页面
            pages = context.pages
            # 打开一个新页面
            page = await context.new_page() if not pages else pages[0]
            # 设置页面视图大小
            await page.set_viewport_size({"width": width, "height": height})
            page.set_default_timeout(1000 * timeout)

            # 打开电影列表
            await self.__movie_list(page)

            # await asyncio.sleep(1000)
            # 关闭页面
            await page.close()
            # 关闭浏览器
            await context.close()