# -*- coding: utf-8 -*-
"""结算流程 UI 自动化测试：登录 → 加购 → 结算 → 下单"""
import allure
from pages.login_page import LoginPage
from pages.product_page import ProductPage
from pages.checkout_page import CheckoutPage


@allure.feature("Checkout Order UI")
class TestCheckoutUI:
    """结算流程测试类"""

    def _login_and_add_to_cart(self, page):
        """登录 testuser 并加购 MacBook，返回 product_page 供后续操作"""
        login_page = LoginPage(page)
        login_page.open()
        login_page.login("testuser_2026@example.com", "Test@12345")

        product_page = ProductPage(page)
        product_page.open()
        product_page.search("MacBook")
        product_page.add_to_cart(0)
        return product_page

    @allure.story("Checkout page accessible")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_checkout_page_accessible(self, page):
        """加购后可进入结算页面"""
        self._login_and_add_to_cart(page)
        checkout_page = CheckoutPage(page)
        checkout_page.checkout()
        checkout_page.screenshot("checkout_accessible")
        assert "route=checkout/checkout" in page.url, f"应进入结算页，实际: {page.url}"

    @allure.story("Payment method selection")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_payment_method_selection(self, page):
        """结算页应提供支付方式选择入口且按钮可点击"""
        self._login_and_add_to_cart(page)
        checkout_page = CheckoutPage(page)
        checkout_page.checkout()
        payment_btn = page.locator("#button-payment-methods")
        assert payment_btn.is_visible(timeout=5000), "结算页应显示支付方式选择按钮"
        payment_btn.click()
        page.wait_for_timeout(2500)
        checkout_page.screenshot("payment_method_selected")
        # 点击后页面应有反馈（配送/地址未完成时会提示先完成配送，否则弹出支付选项）
        feedback = page.locator("#error-payment-method").count() > 0 or \
            page.locator("input[name='payment_method']").count() > 0 or \
            "modal" in page.content().lower()
        assert feedback, "点击支付方式按钮后页面应有反馈"

    @allure.story("Confirm order button")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_confirm_order_button(self, page, db):
        """完成地址/配送/支付选择后点击确认订单，应下单成功且订单落库"""
        self._login_and_add_to_cart(page)
        checkout_page = CheckoutPage(page)
        checkout_page.checkout()
        # 新注册用户无默认地址：填地址 → 选配送 → 选支付 → 确认
        checkout_page.add_shipping_address({
            "firstname": "Test", "lastname": "User",
            "address": "Test Street 123", "city": "Beijing",
            "postcode": "100000", "country": "China", "region": "Beijing",
        })
        checkout_page.choose_shipping_method()
        checkout_page.choose_payment_method()
        checkout_page.confirm_order()
        checkout_page.screenshot("confirm_order")

        # 业务校验：跳转成功页，且订单真实写入 oc_order
        assert checkout_page.is_order_success(), "点击确认订单后应下单成功"
        order = db.query_one("SELECT order_id FROM oc_order ORDER BY order_id DESC LIMIT 1")
        assert order is not None, "下单成功后数据库应存在订单"

    @allure.story("Checkout shows order summary")
    @allure.severity(allure.severity_level.NORMAL)
    def test_checkout_order_summary(self, page):
        """结算页应展示已加购商品与金额汇总"""
        self._login_and_add_to_cart(page)
        checkout_page = CheckoutPage(page)
        checkout_page.checkout()
        checkout_page.screenshot("checkout_summary")
        content = page.content()
        assert "MacBook" in content, "结算页订单摘要应包含已加购商品 MacBook"
        assert "Total" in content, "结算页应展示合计金额"
