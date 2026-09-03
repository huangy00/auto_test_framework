# -*- coding: utf-8 -*-
"""
页面基类：封装所有页面共用的浏览器操作（导航、点击、填表、截图等）。
各业务页面对象继承本类，避免重复代码。
"""
import allure
from playwright.sync_api import Page
from utils.logger import logger
from utils.config_reader import config


class BasePage:
    """页面对象基类"""

    def __init__(self, page: Page):
        self.page = page
        self.timeout = config.getint("DEFAULT", "timeout") * 1000

    def navigate(self, url: str, retries: int = 3):
        """打开指定 URL。

        页面在前一次导航（如登录提交后的 JS 跳转）尚未完成时调用 goto，
        Playwright 会抛 "interrupted by another navigation"。此时先等待当前
        导航稳定，再重试，最多 retries 次。
        """
        logger.info(f"Navigating to {url}")
        for attempt in range(1, retries + 1):
            try:
                self.page.goto(url, wait_until="domcontentloaded", timeout=15000)
                return
            except Exception as e:
                if attempt == retries:
                    raise
                logger.warning(f"Navigation failed (attempt {attempt}/{retries}): {e}")
                try:
                    self.page.wait_for_load_state("domcontentloaded", timeout=10000)
                except Exception:
                    pass

    def click(self, selector: str, timeout: int = None):
        """点击指定元素，失败时自动截图留证"""
        timeout = timeout or self.timeout
        logger.info(f"Clicking: {selector}")
        try:
            self.page.locator(selector).click(timeout=timeout)
        except Exception as e:
            self._screenshot_on_failure("click_failure")
            raise e

    def fill(self, selector: str, value: str, timeout: int = None):
        """向输入框填写内容，失败时自动截图留证"""
        timeout = timeout or self.timeout
        logger.info(f"Filling: {selector} with '{value}'")
        try:
            self.page.locator(selector).fill(value, timeout=timeout)
        except Exception as e:
            self._screenshot_on_failure("fill_failure")
            raise e

    def wait_for_selector(self, selector: str, state: str = "visible", timeout: int = None):
        """等待元素到达指定状态（visible/hidden），返回对应 Locator"""
        timeout = timeout or self.timeout
        logger.info(f"Waiting for: {selector} (state={state})")
        locator = self.page.locator(selector)
        locator.wait_for(state=state, timeout=timeout)
        return locator

    def get_text(self, selector: str, timeout: int = None) -> str:
        """读取指定元素的文本内容"""
        timeout = timeout or self.timeout
        locator = self.wait_for_selector(selector, timeout=timeout)
        return locator.inner_text()

    def is_visible(self, selector: str, timeout: int = 5000) -> bool:
        """判断元素当前是否可见"""
        try:
            self.page.locator(selector).wait_for(state="visible", timeout=timeout)
            return True
        except Exception:
            return False

    def screenshot(self, name: str):
        """截取当前页面并附加到 Allure 报告"""
        screenshot = self.page.screenshot(full_page=True)
        allure.attach(screenshot, name=name, attachment_type=allure.attachment_type.PNG)
        logger.info(f"Screenshot saved: {name}")

    def _screenshot_on_failure(self, name: str):
        """失败时自动截图并附加到 Allure 报告（内部方法）"""
        try:
            screenshot = self.page.screenshot(full_page=True)
            allure.attach(
                screenshot,
                name=f"FAILURE_{name}",
                attachment_type=allure.attachment_type.PNG,
            )
            logger.warning(f"Failure screenshot: {name}")
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
