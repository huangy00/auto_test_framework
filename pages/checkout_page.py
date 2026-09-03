# -*- coding: utf-8 -*-
"""
结算页面对象：封装进入结算页、选择支付方式、确认订单等操作。
"""
from pages.base_page import BasePage
from utils.config_reader import config
from utils.logger import logger


class CheckoutPage(BasePage):
    """结算页面对象"""

    # 元素定位器
    BTN_PAYMENT_METHODS = "#button-payment-methods"  # 选择支付方式按钮
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

    def confirm_order(self):
        """确认订单：点击选择支付方式（若存在）→ 点击确认订单，等待处理完成"""
        logger.info("Confirming order")

        payment_btn = self.page.locator(self.BTN_PAYMENT_METHODS)
        if payment_btn.is_visible(timeout=5000):
            payment_btn.click()
            self.page.wait_for_timeout(2000)

        confirm_btn = self.page.locator(self.BTN_CONFIRM_ORDER)
        if confirm_btn.is_visible(timeout=5000):
            confirm_btn.click()
            self.page.wait_for_load_state("domcontentloaded")
            self.page.wait_for_timeout(3000)

        return self

    def is_order_success(self) -> bool:
        """判断订单是否提交成功（页面是否显示成功标题）"""
        return self.is_visible(self.MSG_ORDER_SUCCESS, timeout=15000)

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
