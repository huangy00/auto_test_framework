# -*- coding: utf-8 -*-
"""
结算页面对象：封装进入结算页、新建配送地址、选择配送/支付方式、确认订单等操作。

注意：OpenCart 4 结算流程对没有默认地址的登录用户要求先填写配送地址；
配送/支付方式通过模态框选择。新注册用户没有地址，因此下单前必须完成
"填地址 -> 选配送 -> 选支付"三步，再点确认订单。
"""
from pages.base_page import BasePage
from utils.config_reader import config
from utils.logger import logger


class CheckoutPage(BasePage):
    """结算页面对象"""

    # 元素定位器
    BTN_SHIPPING_ADDRESS = "#button-shipping-address"  # 保存配送地址
    BTN_SHIPPING_METHODS = "#button-shipping-methods"  # 打开配送方式弹窗
    BTN_SHIPPING_METHOD = "#button-shipping-method"  # 弹窗内确认配送方式
    BTN_PAYMENT_METHODS = "#button-payment-methods"  # 打开支付方式弹窗
    BTN_PAYMENT_METHOD = "#button-payment-method"  # 弹窗内确认支付方式
    BTN_CONFIRM_ORDER = "#button-confirm"  # 确认订单按钮
    INPUT_COMMENT = "#input-comment"  # 订单备注输入框
    MSG_ORDER_SUCCESS = "h1:has-text('Your order has been placed')"  # 下单成功标题

    def checkout(self):
        """进入结算页面"""
        base_url = config.get("ui", "base_url")
        self.navigate(f"{base_url}/index.php?route=checkout/checkout")
        return self

    def fill_billing_details(self, details: dict):
        """填写订单备注（登录用户地址已存在，仅补充 comment）"""
        comment = details.get("comment", "自动化测试订单")
        comment_input = self.page.locator(self.INPUT_COMMENT)
        if comment_input.is_visible(timeout=3000):
            comment_input.fill(comment)
        return self

    def add_shipping_address(self, details: dict):
        """
        填写并保存配送地址（适用于无默认地址的新注册用户）。
        国家/省份需通过下拉选择，选择国家后等待省份列表 AJAX 加载。
        """
        logger.info("Adding shipping address")
        firstname_input = self.page.locator("#input-shipping-firstname")
        if not firstname_input.is_visible(timeout=5000):
            logger.info("配送地址表单不可见（可能已有地址），跳过")
            return self

        firstname_input.fill(details.get("firstname", "Test"))
        self.page.locator("#input-shipping-lastname").fill(details.get("lastname", "User"))
        self.page.locator("#input-shipping-address-1").fill(details.get("address", "Test Street 123"))
        self.page.locator("#input-shipping-city").fill(details.get("city", "Beijing"))
        self.page.locator("#input-shipping-postcode").fill(details.get("postcode", "100000"))

        country = self.page.locator("#input-shipping-country")
        country.select_option(label=details.get("country", "China"))
        self.page.wait_for_timeout(2000)  # 等待省份下拉通过 AJAX 填充
        zone = self.page.locator("#input-shipping-zone")
        if zone.locator("option").count() > 1:
            zone.select_option(label=details.get("region", "Beijing"))
        self.page.wait_for_timeout(500)

        self.click(self.BTN_SHIPPING_ADDRESS)
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_timeout(2000)
        logger.info("Shipping address saved")
        return self

    def _choose_from_modal(self, open_btn_selector: str, radio_value: str,
                           confirm_btn_selector: str, modal_root: str, name: str):
        """打开方式弹窗 -> 选择默认选项(radio 通常已默认选中) -> 确认"""
        open_btn = self.page.locator(open_btn_selector)
        if not open_btn.is_visible(timeout=5000):
            logger.warning(f"{name} 弹窗按钮不可见: {open_btn_selector}")
            return False
        open_btn.click()
        # 等待弹窗内选项出现
        self.page.wait_for_timeout(2500)
        radio = self.page.locator(f"{modal_root} input[name='{name}'][value='{radio_value}']")
        if radio.count():
            if not radio.is_checked():
                radio.check()
        confirm_btn = self.page.locator(confirm_btn_selector)
        if confirm_btn.is_visible(timeout=5000):
            confirm_btn.click()
            self.page.wait_for_load_state("domcontentloaded")
            self.page.wait_for_timeout(2000)
            return True
        logger.warning(f"{name} 确认按钮不可见: {confirm_btn_selector}")
        return False

    def choose_shipping_method(self, code: str = "flat.flat"):
        """选择配送方式（默认 Flat Shipping Rate）"""
        logger.info(f"Choosing shipping method: {code}")
        return self._choose_from_modal(
            self.BTN_SHIPPING_METHODS, code,
            self.BTN_SHIPPING_METHOD, "#modal-shipping", "shipping_method")

    def choose_payment_method(self, code: str = "cod.cod"):
        """选择支付方式（默认 Cash On Delivery）"""
        logger.info(f"Choosing payment method: {code}")
        return self._choose_from_modal(
            self.BTN_PAYMENT_METHODS, code,
            self.BTN_PAYMENT_METHOD, "#modal-payment", "payment_method")

    def confirm_order(self):
        """点击确认订单并等待处理完成（需先完成地址/配送/支付选择）"""
        logger.info("Confirming order")
        confirm_btn = self.page.locator(self.BTN_CONFIRM_ORDER)
        if confirm_btn.is_visible(timeout=10000):
            confirm_btn.click()
            self.page.wait_for_load_state("domcontentloaded")
            self.page.wait_for_timeout(3000)
        else:
            logger.warning("确认订单按钮不可见，下单可能未完成")
        return self

    def is_order_success(self) -> bool:
        """判断订单是否提交成功（页面是否显示成功标题）"""
        return self.is_visible(self.MSG_ORDER_SUCCESS, timeout=20000)

    def get_order_id(self) -> str:
        """从页面 HTML 中提取订单号（匹配 "order #12345" 形式）"""
        try:
            import re
            content = self.page.content()
            match = re.search(r"order\s*#(\d+)", content, re.IGNORECASE)
            if match:
                return match.group(1)
            return ""
        except Exception:
            return ""
