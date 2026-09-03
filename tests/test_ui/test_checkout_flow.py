# -*- coding: utf-8 -*-
"""
UI 自动化测试：完整结算流程
使用 POM 模式测试：注册 → 登录 → 搜索商品 → 加入购物车 → 下单结算
下单成功后调用 db_helper 查询数据库验证订单落库，并附加到 Allure 报告
"""
import json
import os
import allure
import pytest
from pages.register_page import RegisterPage
from pages.login_page import LoginPage
from pages.product_page import ProductPage
from pages.checkout_page import CheckoutPage
from utils.db_helper import db_helper
from utils.logger import logger


# 获取测试数据文件路径
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")


@allure.feature("电商全流程测试")
class TestCheckoutFlow:
    """完整结算流程测试类"""

    @allure.story("注册 → 登录 → 搜索 → 加购 → 下单")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_full_checkout_flow(self, page, test_data):
        """
        测试完整购物流程：
        1. 注册新用户
        2. 登录
        3. 搜索商品
        4. 加入购物车
        5. 下单结算
        6. 数据库验证订单
        """
        # ===== 0. 清理旧用户（确保注册能成功） =====
        with allure.step("步骤0：清理旧测试用户"):
            email = test_data["register_user"]["email"]
            deleted = db_helper.execute(
                "DELETE FROM oc_customer WHERE email = %s", (email,)
            )
            logger.info(f"Cleaned up old user: {email}, deleted={deleted}")

        # ===== 1. 注册用户 =====
        with allure.step("步骤1：注册新用户"):
            register_page = RegisterPage(page)
            register_page.open()
            user = test_data["register_user"]
            register_page.register(
                firstname=user["firstname"],
                lastname=user["lastname"],
                email=user["email"],
                password=user["password"],
            )
            # 截图记录注册结果
            register_page.screenshot("register_result")
            allure.attach(
                f"注册邮箱: {user['email']}",
                name="注册信息",
                attachment_type=allure.attachment_type.TEXT,
            )
            logger.info(f"Registration completed for {user['email']}")

        # ===== 2. 登录 =====
        with allure.step("步骤2：用户登录"):
            login_page = LoginPage(page)
            login_page.open()
            login_page.login(
                email=test_data["login_user"]["email"],
                password=test_data["login_user"]["password"],
            )
            login_page.screenshot("login_result")
            logger.info("Login completed")

        # ===== 3. 搜索商品 =====
        with allure.step("步骤3：搜索商品"):
            product_page = ProductPage(page)
            product_page.open()
            product_page.search(test_data["search_keyword"])
            product_count = product_page.get_product_count()
            product_name = product_page.get_product_name(0)
            product_page.screenshot("search_result")
            allure.attach(
                f"搜索关键词: {test_data['search_keyword']}\n结果数量: {product_count}\n首个商品: {product_name}",
                name="搜索结果",
                attachment_type=allure.attachment_type.TEXT,
            )
            logger.info(f"Found {product_count} products, first: {product_name}")

        # ===== 4. 加入购物车 =====
        with allure.step("步骤4：加入购物车"):
            product_page.add_to_cart(0)
            product_page.screenshot("add_to_cart_result")
            logger.info("Product added to cart")

        # ===== 5. 下单结算 =====
        with allure.step("步骤5：下单结算"):
            checkout_page = CheckoutPage(page)
            checkout_page.checkout()
            checkout_page.fill_billing_details(test_data["checkout"])
            # 新注册用户没有默认地址，需先填配送地址并依次选择配送/支付方式
            checkout_page.add_shipping_address(test_data["checkout"])
            checkout_page.choose_shipping_method()
            checkout_page.choose_payment_method()
            checkout_page.confirm_order()
            checkout_page.screenshot("checkout_result")
            order_success = checkout_page.is_order_success()
            allure.attach(
                f"订单提交状态: {'成功' if order_success else '失败'}",
                name="结算结果",
                attachment_type=allure.attachment_type.TEXT,
            )
            logger.info(f"Order success: {order_success}")

        # ===== 6. 数据库验证 =====
        with allure.step("步骤6：数据库验证订单"):
            # 查询最近的订单记录
            order = db_helper.query_one(
                "SELECT * FROM oc_order ORDER BY order_id DESC LIMIT 1"
            )
            if order:
                order_info = json.dumps(order, default=str, ensure_ascii=False, indent=2)
                allure.attach(
                    order_info,
                    name="数据库订单记录",
                    attachment_type=allure.attachment_type.JSON,
                )
                logger.info(f"Order found in DB: order_id={order.get('order_id')}")
            else:
                allure.attach(
                    "未找到订单记录",
                    name="数据库订单记录",
                    attachment_type=allure.attachment_type.TEXT,
                )
                logger.warning("No order found in database")

            # 断言订单存在
            assert order is not None, "数据库中未找到订单记录"
