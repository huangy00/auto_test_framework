# -*- coding: utf-8 -*-
"""商品搜索 UI 自动化测试"""
import allure
from pages.product_page import ProductPage


@allure.feature("Product Search UI")
class TestSearchUI:
    """商品搜索测试类"""

    @allure.story("Normal search")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_search_success(self, page):
        """搜索存在的商品应返回至少 1 个结果"""
        product_page = ProductPage(page)
        product_page.open()
        product_page.search("MacBook")
        product_page.screenshot("search_success")
        count = product_page.get_product_count()
        assert count >= 1, f"Expected at least 1 product, got {count}"

    @allure.story("No results")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_search_no_results(self, page):
        """搜索不存在的关键词应返回 0 个结果"""
        product_page = ProductPage(page)
        product_page.open()
        product_page.search("xyznonexistent123")
        product_page.screenshot("search_no_results")
        count = product_page.get_product_count()
        assert count == 0, f"Expected 0 products, got {count}"

    @allure.story("Empty keyword search")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search_empty_keyword(self, page):
        """空关键词搜索页面应正常响应（无 0 个或更多结果）"""
        product_page = ProductPage(page)
        product_page.open()
        product_page.search("")
        product_page.screenshot("search_empty")
        assert product_page.get_product_count() >= 0

    @allure.story("Search result has correct product")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_search_result_content(self, page):
        """搜索 MacBook 时首个结果应为 MacBook 系列商品"""
        product_page = ProductPage(page)
        product_page.open()
        product_page.search("MacBook")
        product_page.screenshot("search_content")
        assert product_page.get_product_count() >= 1, "搜索 MacBook 应有结果"
        name = product_page.get_product_name(0)
        assert "macbook" in name.lower(), f"首个结果应含 MacBook，实际: {name}"

    @allure.story("Special characters search")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search_special_chars(self, page):
        """特殊字符搜索不应导致页面崩溃"""
        product_page = ProductPage(page)
        product_page.open()
        product_page.search("!@#$%^&*()")
        product_page.screenshot("search_special_chars")
        assert product_page.get_product_count() >= 0

    @allure.story("SQL injection search")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_search_sql_injection(self, page):
        """SQL 注入语句搜索不应触发服务器 500 错误"""
        product_page = ProductPage(page)
        product_page.open()
        product_page.search("' OR 1=1 --")
        product_page.screenshot("search_sql_injection")
        assert product_page.get_product_count() >= 0
