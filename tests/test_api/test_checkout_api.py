# -*- coding: utf-8 -*-
"""
Checkout / order API tests
"""
import allure
import pytest
from utils.logger import logger


@allure.feature("Checkout Order API")
class TestCheckoutAPI:

    @allure.story("Payment methods")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_payment_methods(self, logged_in_session, site_url):
        response = logged_in_session.get(
            f"{site_url}/index.php?route=checkout/payment_method.getMethods",
        )
        assert response.status_code == 200

    @allure.story("Checkout page")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_checkout_page(self, logged_in_session, site_url):
        response = logged_in_session.get(
            f"{site_url}/index.php?route=checkout/checkout",
        )
        assert response.status_code == 200
        assert "checkout" in response.text.lower() or "payment" in response.text.lower()

    @allure.story("Checkout without login")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.xfail(
        reason="BUG-002: OpenCart 4.1.0.3 未登录访问结算页重定向到购物车页而非登录页，属产品缺陷（见 docs/defect_report）；修复后本用例将 XPASS 提醒",
        strict=True,
    )
    def test_checkout_without_login(self, api_session, site_url):
        response = api_session.get(
            f"{site_url}/index.php?route=checkout/checkout",
            allow_redirects=False,
        )
        assert response.status_code in [301, 302, 200]
        # BUG-002: 未登录应跳转到登录页，而非购物车页
        if response.status_code in [301, 302]:
            location = response.headers.get("Location", "")
            assert "login" in location.lower(), f"Expected redirect to login page, got: {location}"

    @allure.story("Order history")
    @allure.severity(allure.severity_level.NORMAL)
    def test_order_history(self, logged_in_session, site_url):
        response = logged_in_session.get(
            f"{site_url}/index.php?route=account/order",
        )
        assert response.status_code == 200

    @allure.story("Order detail")
    @allure.severity(allure.severity_level.NORMAL)
    def test_order_detail(self, logged_in_session, site_url):
        response = logged_in_session.get(
            f"{site_url}/index.php?route=account/order.info",
            params={"order_id": "1"},
        )
        assert response.status_code in [200, 302]
