# -*- coding: utf-8 -*-
"""
User registration API tests
"""
import uuid
import re
import json
import allure
import pytest
from utils.logger import logger


def _register_token(session, site_url):
    """
    OpenCart 4.x 注册接口带 CSRF 防护：需先 GET 注册页拿到 session 中的
    register_token，再拼到 register.register 的 URL 上提交。
    """
    page = session.get(f"{site_url}/index.php?route=account/register")
    assert page.status_code == 200
    m = re.search(r"register_token=([a-zA-Z0-9]+)", page.text)
    assert m, "注册页未找到 register_token（页面结构可能变化）"
    return m.group(1)


@allure.feature("User Registration API")
class TestRegisterAPI:

    @allure.story("Normal registration")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_register_success(self, api_session, site_url, db):
        unique_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        data = {
            "firstname": "Test",
            "lastname": "User",
            "email": unique_email,
            "telephone": "13800138000",
            "password": "Test@12345",
            "agree": "1",
        }
        token = _register_token(api_session, site_url)
        response = api_session.post(
            f"{site_url}/index.php?route=account/register.register&register_token={token}",
            data=data,
            allow_redirects=False,
        )
        logger.info(f"Register response: {response.status_code}")
        assert response.status_code in [200, 302]
        # 业务校验 1：注册成功应跳转到 account/success（而非停留在注册页）
        redirect_url = json.loads(response.text).get("redirect", "")
        assert "route=account/success" in redirect_url, f"注册应跳转到成功页，实际: {redirect_url}"
        # 业务校验 2：新用户必须真实写入 oc_customer 表
        user = db.query_one(
            "SELECT customer_id FROM oc_customer WHERE email = %s",
            (unique_email,),
        )
        assert user is not None, f"注册接口返回成功，但数据库未找到用户 {unique_email}"

    @allure.story("Duplicate email")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_register_duplicate_email(self, api_session, site_url):
        data = {
            "firstname": "Test",
            "lastname": "User",
            "email": "testuser_2026@example.com",
            "telephone": "13800138000",
            "password": "Test@12345",
        }
        token = _register_token(api_session, site_url)
        response = api_session.post(
            f"{site_url}/index.php?route=account/register.register&register_token={token}",
            data=data,
            allow_redirects=False,
        )
        assert response.status_code == 200
        # 业务校验：已存在的邮箱应被拒绝并返回错误，而不是跳转成功页
        assert "route=account/success" not in response.text
        assert "error" in response.text.lower(), "重复邮箱注册应返回错误信息"

    @allure.story("Empty email")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_register_empty_email(self, api_session, site_url):
        data = {
            "firstname": "Test",
            "lastname": "User",
            "email": "",
            "telephone": "13800138000",
            "password": "Test@12345",
        }
        response = api_session.post(
            f"{site_url}/index.php?route=account/register.register",
            data=data,
        )
        assert response.status_code == 200

    @allure.story("Empty password")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_register_empty_password(self, api_session, site_url):
        data = {
            "firstname": "Test",
            "lastname": "User",
            "email": "newuser@example.com",
            "telephone": "13800138000",
            "password": "",
        }
        response = api_session.post(
            f"{site_url}/index.php?route=account/register.register",
            data=data,
        )
        assert response.status_code == 200

    @allure.story("Invalid email format")
    @allure.severity(allure.severity_level.NORMAL)
    def test_register_invalid_email(self, api_session, site_url):
        data = {
            "firstname": "Test",
            "lastname": "User",
            "email": "invalidemail",
            "telephone": "13800138000",
            "password": "Test@12345",
        }
        response = api_session.post(
            f"{site_url}/index.php?route=account/register.register",
            data=data,
        )
        assert response.status_code == 200

    @allure.story("SQL injection")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_register_sql_injection(self, api_session, site_url):
        data = {
            "firstname": "Test",
            "lastname": "User",
            "email": "' OR 1=1 --@test.com",
            "telephone": "13800138000",
            "password": "Test@12345",
        }
        response = api_session.post(
            f"{site_url}/index.php?route=account/register.register",
            data=data,
        )
        assert response.status_code != 500

    @allure.story("XSS injection")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_register_xss(self, api_session, site_url):
        data = {
            "firstname": "<script>alert(1)</script>",
            "lastname": "User",
            "email": "xss_test@example.com",
            "telephone": "13800138000",
            "password": "Test@12345",
        }
        response = api_session.post(
            f"{site_url}/index.php?route=account/register.register",
            data=data,
        )
        assert response.status_code != 500
