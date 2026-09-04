# -*- coding: utf-8 -*-
"""购物车 UI 自动化测试：登录后搜索商品、加购、查看购物车"""
import allure
from pages.login_page import LoginPage
from pages.product_page import ProductPage


@allure.feature("Shopping Cart UI")
class TestCartUI:
    """购物车测试类"""

    @allure.story("Add to cart success")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_add_to_cart_success(self, page):
        """登录后搜索并加购商品，应显示加购成功提示"""
        login_page = LoginPage(page)
        login_page.open()
        login_page.login("testuser_2026@example.com", "Test@12345")

        product_page = ProductPage(page)
        product_page.open()
        product_page.search("MacBook")
        product_page.add_to_cart(0)  # 加购第一个搜索结果
        product_page.screenshot("cart_add_success")

        assert product_page.is_cart_success(), "加购后应出现成功提示"

    @allure.story("View cart")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_view_cart(self, page):
        """加购后点击查看购物车，应进入购物车页面"""
        login_page = LoginPage(page)
        login_page.open()
        login_page.login("testuser_2026@example.com", "Test@12345")

        product_page = ProductPage(page)
        product_page.open()
        product_page.search("MacBook")
        product_page.add_to_cart(0)
        product_page.go_to_cart()
        product_page.screenshot("cart_view")

        assert "route=checkout/cart" in page.url, f"应进入购物车页，实际: {page.url}"

    @allure.story("Cart shows correct item")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_cart_shows_item(self, page):
        """加购后购物车应展示该商品（MacBook）"""
        login_page = LoginPage(page)
        login_page.open()
        login_page.login("testuser_2026@example.com", "Test@12345")

        product_page = ProductPage(page)
        product_page.open()
        product_page.search("MacBook")
        product_page.add_to_cart(0)
        product_page.go_to_cart()
        product_page.screenshot("cart_shows_item")

        assert "MacBook" in page.content(), "购物车页应包含已加购商品 MacBook"

    @allure.story("Add multiple products")
    @allure.severity(allure.severity_level.NORMAL)
    def test_add_multiple_products(self, page):
        """连续加购 MacBook 与 iPhone 两个不同商品"""
        login_page = LoginPage(page)
        login_page.open()
        login_page.login("testuser_2026@example.com", "Test@12345")

        product_page = ProductPage(page)
        product_page.open()
        product_page.search("MacBook")
        product_page.add_to_cart(0)

        product_page.search("iPhone")
        if product_page.get_product_count() > 0:
            product_page.add_to_cart(0)

        product_page.screenshot("cart_multiple")
        assert product_page.is_cart_success(), "加购多个商品后应出现成功提示"
