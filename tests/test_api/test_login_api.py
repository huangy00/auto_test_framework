# -*- coding: utf-8 -*-
"""
User login API tests
"""
import allure
import pytest
from utils.logger import logger


@allure.feature("User Login API")
class TestLoginAPI:

    @allure.story("Normal login")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_login_success(self, api_session, site_url):
        data = {
            "email": "testuser_2026@example.com",
            "password": "Test@12345",
        }
        response = api_session.post(
            f"{site_url}/index.php?route=account/login.login",
            data=data,
        )
        logger.info(f"Login response: {response.status_code}")
        assert response.status_code in [200, 302]
        # 业务校验：登录成功后会话应有效，账户页可访问并展示 My Account
        account = api_session.get(
            f"{site_url}/index.php?route=account/account",
        )
        assert account.status_code == 200
        assert "my account" in account.text.lower(), "登录成功后应能访问账户页 (My Account)"

    @allure.story("Wrong password")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_wrong_password(self, api_session, site_url):
        data = {
            "email": "testuser_2026@example.com",
            "password": "wrongpassword",
        }
        response = api_session.post(
            f"{site_url}/index.php?route=account/login.login",
            data=data,
        )
        assert response.status_code == 200
        # OpenCart 4.x returns JSON redirect back to login page on failure
        assert "login" in response.text.lower() or "error" in response.text.lower()

    @allure.story("Nonexistent user")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_nonexistent_user(self, api_session, site_url):
        data = {
            "email": "nonexistent@example.com",
            "password": "Test@12345",
        }
        response = api_session.post(
            f"{site_url}/index.php?route=account/login.login",
            data=data,
        )
        assert response.status_code == 200
        assert "login" in response.text.lower() or "error" in response.text.lower()

    @allure.story("Empty email")
    @allure.severity(allure.severity_level.NORMAL)
    def test_login_empty_email(self, api_session, site_url):
        data = {
            "email": "",
            "password": "Test@12345",
        }
        response = api_session.post(
            f"{site_url}/index.php?route=account/login.login",
            data=data,
        )
        assert response.status_code == 200

    @allure.story("Empty password")
    @allure.severity(allure.severity_level.NORMAL)
    def test_login_empty_password(self, api_session, site_url):
        data = {
            "email": "testuser_2026@example.com",
            "password": "",
        }
        response = api_session.post(
            f"{site_url}/index.php?route=account/login.login",
            data=data,
        )
        assert response.status_code == 200

    @allure.story("SQL injection")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_login_sql_injection(self, api_session, site_url):
        data = {
            "email": "' OR 1=1 --",
            "password": "anything",
        }
        response = api_session.post(
            f"{site_url}/index.php?route=account/login.login",
            data=data,
        )
        assert response.status_code != 500

    @allure.story("XSS injection")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_login_xss(self, api_session, site_url):
        data = {
            "email": "<script>alert(1)</script>",
            "password": "anything",
        }
        response = api_session.post(
            f"{site_url}/index.php?route=account/login.login",
            data=data,
        )
        assert response.status_code != 500
