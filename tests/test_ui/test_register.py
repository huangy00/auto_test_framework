# -*- coding: utf-8 -*-
"""
Register UI tests
"""
import uuid
import allure
import pytest
from pages.register_page import RegisterPage
from utils.db_helper import db_helper
from utils.logger import logger


@allure.feature("User Register UI")
class TestRegisterUI:

    @allure.story("Normal register")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_register_success(self, page):
        """Register with valid data should succeed and persist the user"""
        unique_email = f"ui_test_{uuid.uuid4().hex[:8]}@example.com"
        register_page = RegisterPage(page)
        register_page.open()
        register_page.register(
            firstname="UI",
            lastname="Test",
            email=unique_email,
            password="Test@12345",
        )
        register_page.screenshot("register_success")
        # 注册成功应跳转到成功页(account/success)
        assert "success" in page.url or "account" in page.url, \
            f"注册成功应跳转成功页，实际: {page.url}"
        # 业务校验：新用户必须真实写入 oc_customer 表
        user = db_helper.query_one(
            "SELECT customer_id FROM oc_customer WHERE email = %s", (unique_email,)
        )
        assert user is not None, f"注册成功但数据库未找到用户 {unique_email}"

    @allure.story("Duplicate email")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_register_duplicate_email(self, page):
        """Register with existing email, should show error"""
        register_page = RegisterPage(page)
        register_page.open()
        register_page.register(
            firstname="Test",
            lastname="User",
            email="testuser_2026@example.com",
            password="Test@12345",
        )
        register_page.screenshot("register_duplicate")
        assert register_page.is_error_displayed() or "register" in page.url

    @allure.story("Empty firstname")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_register_empty_firstname(self, page):
        """Register with empty firstname, should show error"""
        register_page = RegisterPage(page)
        register_page.open()
        register_page.register(
            firstname="",
            lastname="User",
            email=f"test_{uuid.uuid4().hex[:8]}@example.com",
            password="Test@12345",
        )
        register_page.screenshot("register_empty_firstname")
        assert register_page.is_error_displayed() or "register" in page.url

    @allure.story("Empty email")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_register_empty_email(self, page):
        """Register with empty email, should show error"""
        register_page = RegisterPage(page)
        register_page.open()
        register_page.register(
            firstname="Test",
            lastname="User",
            email="",
            password="Test@12345",
        )
        register_page.screenshot("register_empty_email")
        assert register_page.is_error_displayed() or "register" in page.url

    @allure.story("Empty password")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_register_empty_password(self, page):
        """Register with empty password, should show error"""
        register_page = RegisterPage(page)
        register_page.open()
        register_page.register(
            firstname="Test",
            lastname="User",
            email=f"test_{uuid.uuid4().hex[:8]}@example.com",
            password="",
        )
        register_page.screenshot("register_empty_password")
        assert register_page.is_error_displayed() or "register" in page.url

    @allure.story("Invalid email format")
    @allure.severity(allure.severity_level.NORMAL)
    def test_register_invalid_email(self, page):
        """Register with invalid email format, should show error"""
        register_page = RegisterPage(page)
        register_page.open()
        register_page.register(
            firstname="Test",
            lastname="User",
            email="invalidemail",
            password="Test@12345",
        )
        register_page.screenshot("register_invalid_email")
        assert register_page.is_error_displayed() or "register" in page.url

    @allure.story("All fields empty")
    @allure.severity(allure.severity_level.NORMAL)
    def test_register_all_empty(self, page):
        """Register with all fields empty, should show error"""
        register_page = RegisterPage(page)
        register_page.open()
        register_page.register(
            firstname="",
            lastname="",
            email="",
            password="",
        )
        register_page.screenshot("register_all_empty")
        assert register_page.is_error_displayed() or "register" in page.url
