# -*- coding: utf-8 -*-
"""
商品页面对象：封装商品搜索、加入购物车、查看购物车等操作。
"""
from pages.base_page import BasePage
from utils.config_reader import config
from utils.logger import logger


class ProductPage(BasePage):
    """商品页面对象"""

    # 元素定位器
    # 顶部搜索框需精确匹配，避免与搜索结果页的搜索框冲突（见 BUG-002）
    INPUT_SEARCH = "form[action*='search.redirect'] input[name='search']"
    BTN_SEARCH = "button[type='button']"  # 搜索按钮
    LIST_PRODUCTS = ".product-thumb"  # 商品卡片容器
    PRODUCT_NAME = ".product-thumb h4 a"  # 商品名称链接
    PRODUCT_PRICE = ".product-thumb .price"  # 商品价格
    # 用 formaction 定位加购按钮：Bootstrap tooltip 触发后 title 属性被移除，常规属性定位会失败
    BTN_ADD_CART = "button[formaction*='cart.add']"
    MSG_CART_SUCCESS = ".alert-success"  # 加购成功提示
    BTN_VIEW_CART = "a[title='Shopping Cart']"  # 查看购物车

    def open(self):
        """打开首页"""
        base_url = config.get("ui", "base_url")
        self.navigate(f"{base_url}")
        return self

    def search(self, keyword: str):
        """输入关键词并回车搜索（回车提交比点击按钮更稳定）"""
        logger.info(f"Searching product: {keyword}")
        self.fill(self.INPUT_SEARCH, keyword)
        self.page.locator(self.INPUT_SEARCH).press("Enter")
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_timeout(1000)
        return self

    def get_product_count(self) -> int:
        """返回搜索结果中的商品数量"""
        return len(self.page.locator(self.LIST_PRODUCTS).all())

    def get_product_name(self, index: int = 0) -> str:
        """返回指定下标（从 0 开始）的商品名称"""
        return self.page.locator(self.PRODUCT_NAME).nth(index).inner_text()

    def add_to_cart(self, index: int = 0):
        """将指定下标的商品加入购物车，并等待加购成功提示"""
        logger.info(f"Adding product at index {index} to cart")
        self.page.locator(self.BTN_ADD_CART).nth(index).click()
        self.wait_for_selector(self.MSG_CART_SUCCESS, timeout=5000)
        return self

    def go_to_cart(self):
        """点击查看购物车"""
        self.click(self.BTN_VIEW_CART)
        self.page.wait_for_load_state("domcontentloaded")
        return self

    def is_cart_success(self) -> bool:
        """判断加购是否成功（成功提示框是否显示）"""
        return self.is_visible(self.MSG_CART_SUCCESS, timeout=5000)
