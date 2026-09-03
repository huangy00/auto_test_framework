# -*- coding: utf-8 -*-
"""
Shopping cart API tests
"""
import allure
import pytest
from utils.logger import logger


@allure.feature("Shopping Cart API")
class TestCartAPI:

    @allure.story("Add to cart")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_add_to_cart_success(self, logged_in_session, site_url):
        data = {
            "product_id": "43",
            "quantity": "1",
        }
        response = logged_in_session.post(
            f"{site_url}/index.php?route=checkout/cart.add",
            data=data,
        )
        logger.info(f"Add to cart response: {response.status_code}")
        assert response.status_code == 200
        # 业务校验：加购接口成功后，购物车页应能查到该商品（43 为演示数据 MacBook）
        cart_page = logged_in_session.get(
            f"{site_url}/index.php?route=checkout/cart",
        )
        assert cart_page.status_code == 200
        assert "macbook" in cart_page.text.lower(), "加购成功后购物车应包含 MacBook"

    @allure.story("Zero quantity")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_add_to_cart_zero_quantity(self, logged_in_session, site_url):
        data = {
            "product_id": "43",
            "quantity": "0",
        }
        response = logged_in_session.post(
            f"{site_url}/index.php?route=checkout/cart.add",
            data=data,
        )
        assert response.status_code in [200, 400]

    @allure.story("Negative quantity")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_add_to_cart_negative_quantity(self, logged_in_session, site_url):
        data = {
            "product_id": "43",
            "quantity": "-1",
        }
        response = logged_in_session.post(
            f"{site_url}/index.php?route=checkout/cart.add",
            data=data,
        )
        assert response.status_code in [200, 400]

    @allure.story("Exceed stock")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_add_to_cart_exceed_stock(self, logged_in_session, site_url):
        data = {
            "product_id": "43",
            "quantity": "99999",
        }
        response = logged_in_session.post(
            f"{site_url}/index.php?route=checkout/cart.add",
            data=data,
        )
        assert response.status_code in [200, 400]

    @allure.story("Product not found")
    @allure.severity(allure.severity_level.NORMAL)
    def test_add_to_cart_not_found(self, logged_in_session, site_url):
        data = {
            "product_id": "999999",
            "quantity": "1",
        }
        response = logged_in_session.post(
            f"{site_url}/index.php?route=checkout/cart.add",
            data=data,
        )
        assert response.status_code in [200, 400]

    @allure.story("View cart")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_view_cart(self, logged_in_session, site_url):
        response = logged_in_session.get(
            f"{site_url}/index.php?route=checkout/cart",
        )
        assert response.status_code == 200

    @allure.story("Cart info AJAX")
    @allure.severity(allure.severity_level.NORMAL)
    def test_cart_info(self, logged_in_session, site_url):
        response = logged_in_session.get(
            f"{site_url}/index.php?route=common/cart.info",
        )
        assert response.status_code == 200
