# -*- coding: utf-8 -*-
"""
注册页面对象模块
封装 OpenCart 注册页面的元素定位和操作方法
定位器参考 OpenCart 4.x 注册页面
"""
from pages.base_page import BasePage
from utils.config_reader import config
from utils.logger import logger


class RegisterPage(BasePage):
    """OpenCart 注册页面对象"""

    # 页面元素定位器
    INPUT_FIRSTNAME = "#input-firstname"      # 名字输入框
    INPUT_LASTNAME = "#input-lastname"        # 姓氏输入框
    INPUT_EMAIL = "#input-email"              # 邮箱输入框
    INPUT_PASSWORD = "#input-password"        # 密码输入框
    BTN_CONTINUE = "button.btn-primary[type='submit']"  # 注册按钮（Continue）
    MSG_SUCCESS = ".alert-success"            # 注册成功提示
    MSG_ERROR = ".alert-danger"               # 注册失败提示
    LINK_LOGIN = "a:has-text('login')"        # 登录链接

    def open(self):
        """打开注册页面"""
        base_url = config.get("ui", "base_url")
        self.navigate(f"{base_url}/index.php?route=account/register")
        logger.info("Register page opened")
        return self

    def register(self, firstname: str, lastname: str, email: str, password: str):
        """
        执行注册操作
        :param firstname: 名字
        :param lastname: 姓氏
        :param email: 邮箱
        :param password: 密码
        """
        logger.info(f"Registering user: {email}")
        self.fill(self.INPUT_FIRSTNAME, firstname)
        self.fill(self.INPUT_LASTNAME, lastname)
        self.fill(self.INPUT_EMAIL, email)
        self.fill(self.INPUT_PASSWORD, password)

        # 勾选隐私政策（如果有复选框的话）
        privacy_checkbox = self.page.locator("input[name='agree']")
        if privacy_checkbox.is_visible(timeout=2000):
            privacy_checkbox.check()

        self.click(self.BTN_CONTINUE)
        # 注册提交为 AJAX + JS 跳转，等待页面稳定，避免后续立即导航竞争
        self.page.wait_for_timeout(500)
        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=15000)
        except Exception:
            logger.warning("注册提交后页面未完成跳转（可能为注册失败场景）")
        return self

    def is_register_success(self) -> bool:
        """判断注册是否成功"""
        return self.is_visible(self.MSG_SUCCESS, timeout=5000)

    def is_error_displayed(self) -> bool:
        """判断是否显示错误信息"""
        return self.is_visible(self.MSG_ERROR, timeout=3000)

    def get_error_message(self) -> str:
        """获取错误信息文本"""
        return self.get_text(self.MSG_ERROR)

    def get_success_message(self) -> str:
        """获取成功信息文本"""
        return self.get_text(self.MSG_SUCCESS)
