# -*- coding: utf-8 -*-
"""
登录页面对象
作用：把登录页面的所有操作封装成函数，测试脚本直接调用
"""
from pages.base_page import BasePage
from utils.config_reader import config
from utils.logger import logger


class LoginPage(BasePage):
    """登录页面对象，继承 BasePage 获得基础操作能力"""

    # 元素定位器
    INPUT_EMAIL = "#input-email"  # 邮箱输入框
    INPUT_PASSWORD = "#input-password"  # 密码输入框
    BTN_LOGIN = "button.btn-primary[type='submit']"  # 登录按钮
    MSG_ERROR = ".alert-danger"  # 错误提示框
    MSG_SUCCESS = ".alert-success"  # 成功提示框
    LINK_REGISTER = "a:has-text('Register')"  # 跳转注册页链接
    LINK_ACCOUNT = "a:has-text('My Account')"  # 登录后顶部账户链接

    def open(self):
        """打开登录页面"""
        base_url = config.get("ui", "base_url")
        self.navigate(f"{base_url}/index.php?route=account/login")
        logger.info("Login page opened")
        return self

    def login(self, email: str, password: str):
        """填写邮箱密码并提交登录表单。

        OpenCart 4 登录为 AJAX 提交 + JS 跳转，点击后等待页面稳定，
        避免后续立即 navigate 与登录跳转产生导航竞争。
        """
        logger.info(f"Logging in with: {email}")
        self.fill(self.INPUT_EMAIL, email)
        self.fill(self.INPUT_PASSWORD, password)
        self.click(self.BTN_LOGIN)
        self.page.wait_for_timeout(500)
        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=15000)
        except Exception:
            logger.warning("登录提交后页面未完成跳转（可能为登录失败场景）")
        return self

    def is_login_success(self) -> bool:
        """登录成功后页面出现顶部账户链接，以此判断是否成功"""
        return self.is_visible(self.LINK_ACCOUNT, timeout=5000)

    def is_error_displayed(self) -> bool:
        """登录失败时页面出现错误提示框"""
        return self.is_visible(self.MSG_ERROR, timeout=3000)

    def get_error_message(self) -> str:
        """获取错误提示的文本内容"""
        return self.get_text(self.MSG_ERROR)

    def click_register(self):
        """点击注册链接"""
        self.click(self.LINK_REGISTER)
        return self
