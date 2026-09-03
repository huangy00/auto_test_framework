# -*- coding: utf-8 -*-
"""
Product search API tests
"""
import allure
import pytest
from utils.logger import logger


@allure.feature("Product Search API")
class TestSearchAPI:

    @allure.story("Normal search")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_search_success(self, api_session, site_url):
        response = api_session.get(
            f"{site_url}/index.php?route=product/search",
            params={"search": "MacBook"},
        )
        assert response.status_code == 200
        # 业务校验：搜索 "MacBook" 必须真实命中 MacBook 商品，而非仅返回任意页面
        assert "macbook" in response.text.lower()

    @allure.story("No results")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_search_no_results(self, api_session, site_url):
        response = api_session.get(
            f"{site_url}/index.php?route=product/search",
            params={"search": "xyznonexistent123"},
        )
        assert response.status_code == 200
        assert "no product" in response.text.lower() or "not found" in response.text.lower() or "0 result" in response.text.lower()

    @allure.story("Empty keyword")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search_empty_keyword(self, api_session, site_url):
        response = api_session.get(
            f"{site_url}/index.php?route=product/search",
            params={"search": ""},
        )
        assert response.status_code == 200
        assert "no product" in response.text.lower() or "enter a product name" in response.text.lower()

    @allure.story("SQL injection")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_search_sql_injection(self, api_session, site_url):
        response = api_session.get(
            f"{site_url}/index.php?route=product/search",
            params={"search": "' OR 1=1 --"},
        )
        assert response.status_code != 500

    @allure.story("XSS injection")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_search_xss(self, api_session, site_url):
        response = api_session.get(
            f"{site_url}/index.php?route=product/search",
            params={"search": "<script>alert(1)</script>"},
        )
        assert response.status_code != 500

    @allure.story("Special characters")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search_special_chars(self, api_session, site_url):
        response = api_session.get(
            f"{site_url}/index.php?route=product/search",
            params={"search": "!@#$%^&*()"},
        )
        assert response.status_code == 200

    @allure.story("Long keyword")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search_long_keyword(self, api_session, site_url):
        response = api_session.get(
            f"{site_url}/index.php?route=product/search",
            params={"search": "a" * 1000},
        )
        assert response.status_code in [200, 400, 414]
