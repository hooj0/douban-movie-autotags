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

    def __parse_tag(self, text_list, prefix, index=None):
        text = self.__find_tag(text_list, prefix)

        if text is None:
            self.log.error("Could not find tag: ", prefix)
            return None

        if text.count("/") > 0:
            tags = text.replace(" ", "").split("/")
            if index is not None:
                return tags[index]
            else:
                return " ".join(tags)
        else:
            return text.strip()

    async def __changed_tag(self, page):
        info_el = page.locator("div.article div#info")
        info_contents = (await info_el.inner_text()).split("\n")

        tags_name = const.TAGS
        category = self.__parse_tag(info_contents, "类型: ")
        country = self.__parse_tag(info_contents, "制片国家/地区: ", index=0)
        tag_text = tags_name + " " + country + " " + category

        mark_tag_el = page.locator("div#interest_sect_level")
        source_type = await mark_tag_el.inner_text()
        if source_type.count("电视剧") != 0:
            tag_text = tag_text + " 电视剧"
        self.log.debug("movie detail:", info_contents)
        self.log.debug("movie type:", category)
        self.log.debug("movie country:", country)
        self.log.debug("movie tag:", tag_text)

        await mark_tag_el.locator("a:has-text('修改')").click()
        try:
            await page.wait_for_selector("div#dialog input[name=tags]")
        except TimeoutError as e:
            self.log.error("open dialog timeout, reopening dialog")
            await page.screenshot()
            await mark_tag_el.locator("a:has-text('修改')").click()
            await page.wait_for_selector("div#dialog input[name=tags]")

        self.log.info("open dialog success")

        dialog_el = page.locator("div#dialog")
        await dialog_el.locator("input[name=tags]").fill(tag_text)
        await dialog_el.locator("input:has-text('保存') >> visible=true").click()
        await page.wait_for_selector("div#submits", timeout=0, state="detached")
        self.log.info("save tag success\n")

        # await asyncio.sleep(random.randrange(1, 3))

    async def __open_movie(self, page, movie_el):
        movie_name = await movie_el.locator("li.title a em").inner_text()
        tagged_count = await movie_el.locator("span.tags:text('%s')" % const.TAGS).count()
        if tagged_count != 1:
            self.log.info("open movie: %s" % movie_name)

            await movie_el.locator("li.title a").click()
            await page.wait_for_load_state(state="domcontentloaded")

            title = await page.title()
            if title == "页面不存在":
                self.log.error("movie detail is not exist\n")
                await page.go_back()
                return None

            try:
                await page.wait_for_selector("div#info")
            except TimeoutError as e:
                self.log.error("open movie timeout, reload page")
                await page.screenshot()
                await page.reload()
                await page.wait_for_selector("div#info")

            self.log.debug("movie detail load success")

            await self.__changed_tag(page)
            try:
                await page.go_back()
            except:
                self.log.error("go back error", sys.exc_info()[0])
                await page.screenshot()
                await page.go_back()
        else:
            self.log.debug("tagged movie:", movie_name)

    async def __movie_list(self, page):
        await page.wait_for_load_state()
        await page.wait_for_selector("div.article", timeout=0)
        self.log.debug("movie list load success\n")

        paginator_el = page.locator("div.article div.paginator")
        page_current = await paginator_el.locator("span.thispage").inner_text()
        page_total = await paginator_el.locator("span.thispage").get_attribute("data-total-page")
        self.log.info("current page: %s, total page: %s" % (page_current, page_total))

        tags_name = const.TAGS
        tagged_el = page.locator("div.grid-view div.item", has=page.locator("span.tags:text('%s')" % tags_name))
        tagged_el_count = await tagged_el.count()
        if tagged_el_count >= 15:
            self.log.warn("already mark tag count：%s" % tagged_el_count)
        else:
            self.log.debug("wait for the tags to be added count：%s" % tagged_el_count)

        movie_els = page.locator("div.grid-view div.item")
        movie_els_count = await movie_els.count()
        self.log.debug("found movies count: %d" % movie_els_count)

        for i in range(movie_els_count):
            movie_el = movie_els.nth(i)

            await self.__open_movie(page, movie_el)

        if page_current == page_total:
            exit("Mark tag complete.")
        else:
            self.log.warn("next page")
            await paginator_el.locator("span.next a").click()
            await self.__movie_list(page)

    async def __open_page(self, page):
        category = "wish" if not const.VIEWED else "collect"
        # 设置请求URL
        url = f"https://movie.douban.com/people/{const.USER}/{category}"

        # 地址栏跳转到当前网址
        response = await page.goto(url, timeout=0)
        self.log.debug("request url:", url)
        self.log.debug("response url:", response.url)
        self.log.info("open page: %s, ok: %s" % (await page.title(), response.ok))

        await self.__movie_list(page)

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
            await self.__open_page(page)

            # await asyncio.sleep(1000)
            # 关闭页面
            await page.close()
            # 关闭浏览器
            await context.close()