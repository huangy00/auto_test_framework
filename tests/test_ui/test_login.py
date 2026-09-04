# -*- coding: utf-8 -*-
"""登录页面 UI 自动化测试"""
import allure
from pages.login_page import LoginPage


@allure.feature("User Login UI")
class TestLoginUI:
    """登录页面测试类"""

    @allure.story("Normal login")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_login_success(self, page):
        """正确账号密码应登录成功并进入账户页（My Account）"""
        login_page = LoginPage(page)
        login_page.open()
        login_page.login("testuser_2026@example.com", "Test@12345")
        login_page.screenshot("login_success")

        # 登录成功应跳转到账户页，而不是停留在 account/login
        assert "/account/account" in page.url or "route=account/account" in page.url, \
            f"登录成功应跳转账户页，实际: {page.url}"
        assert "my account" in page.content().lower(), "账户页应显示 My Account"

    @allure.story("Wrong password")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_wrong_password(self, page):
        """错误密码应显示错误提示框"""
        login_page = LoginPage(page)
        login_page.open()
        login_page.login("testuser_2026@example.com", "wrongpassword")
        login_page.screenshot("login_wrong_password")
        assert login_page.is_error_displayed(), "错误密码登录应显示错误提示"

    @allure.story("Nonexistent user")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_nonexistent_user(self, page):
        """不存在的账号应显示错误提示框"""
        login_page = LoginPage(page)
        login_page.open()
        login_page.login("nonexistent@example.com", "Test@12345")
        login_page.screenshot("login_nonexistent")
        assert login_page.is_error_displayed(), "不存在的账号登录应显示错误提示"

    @allure.story("Empty email")
    @allure.severity(allure.severity_level.NORMAL)
    def test_login_empty_email(self, page):
        """邮箱为空应显示错误提示或停留在登录页"""
        login_page = LoginPage(page)
        login_page.open()
        login_page.login("", "Test@12345")
        login_page.screenshot("login_empty_email")
        assert login_page.is_error_displayed() or "account/login" in page.url

    @allure.story("Empty password")
    @allure.severity(allure.severity_level.NORMAL)
    def test_login_empty_password(self, page):
        """密码为空应显示错误提示或停留在登录页"""
        login_page = LoginPage(page)
        login_page.open()
        login_page.login("testuser_2026@example.com", "")
        login_page.screenshot("login_empty_password")
        assert login_page.is_error_displayed() or "account/login" in page.url

    @allure.story("Empty form submit")
    @allure.severity(allure.severity_level.NORMAL)
    def test_login_empty_form(self, page):
        """邮箱密码均为空应显示错误提示或停留在登录页"""
        login_page = LoginPage(page)
        login_page.open()
        login_page.login("", "")
        login_page.screenshot("login_empty_form")
        assert login_page.is_error_displayed() or "account/login" in page.url
