# -*- coding: utf-8 -*-
"""
为全新 OpenCart 环境准备可下单的结算条件（幂等，CI / 新环境在测试前执行）。

背景：OpenCart 演示数据（install/opencart-en-gb.sql）只注册扩展（oc_extension），
oc_extension_install 与支付开关设置（oc_setting 的 payment_*_status）缺失；
且演示商品 MacBook（product_id=43，搜索 "MacBook" 的默认下单商品）shipping=0，
购物车无配送需求时货到付款（cod）等支付方式不可用，导致结算无法下单。
本地环境曾由 setup.py / 后台手工补过，CI / 新环境需调用本脚本。

本脚本会：
  1. 登记并启用支付扩展（oc_extension_install + oc_setting payment_*_status）
  2. 将测试下单商品（product_id=43 MacBook）标记为需要配送（shipping=1）

用法：
    python scripts/enable_payment_extensions.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config_reader import config  # noqa: E402
from utils.db_helper import db_helper  # noqa: E402
from utils.logger import logger  # noqa: E402

PAYMENTS = ["cod", "free_checkout"]

# 每个支付方式需要写入门店设置（getMethods 依据 payment_<code>_status 判定启用）
PAYMENT_SETTINGS = {
    "cod": {
        "payment_cod_status": "1",
        "payment_cod_order_status_id": "1",
        "payment_cod_sort_order": "5",
        "payment_cod_total": "0.01",
        "payment_cod_geo_zone_id": "0",
    },
    "free_checkout": {
        "payment_free_checkout_status": "1",
        "payment_free_checkout_order_status_id": "1",
        "payment_free_checkout_sort_order": "1",
    },
}


def _insert_setting(code: str, key: str, value: str):
    """向 oc_setting 插入一条门店设置（不存在才插入）"""
    row = db_helper.query_one(
        "SELECT setting_id FROM oc_setting WHERE code = %s AND `key` = %s",
        (code, key),
    )
    if row:
        return False
    db_helper.execute(
        "INSERT INTO oc_setting (store_id, code, `key`, `value`, serialized) "
        "VALUES (0, %s, %s, %s, 0)",
        (code, key, value),
    )
    return True


def ensure_product_shipping() -> None:
    """
    将测试下单商品（演示数据 product_id=43 = MacBook）标记为需要配送。
    演示数据中该商品 shipping=0，购物车 hasShipping=false，
    货到付款等支付方式会被跳过，导致结算无法下单。
    """
    row = db_helper.query_one(
        "SELECT product_id, shipping FROM oc_product WHERE product_id = 43"
    )
    if row and row["shipping"] == 0:
        db_helper.execute(
            "UPDATE oc_product SET shipping = 1 WHERE product_id = 43"
        )
        logger.info("已标记 product_id=43 (MacBook) 需要配送: shipping=1")
    else:
        logger.info("product_id=43 (MacBook) 无需处理 (shipping 已为 1 或商品不存在)")


def main() -> int:
    ensure_product_shipping()
    for code in PAYMENTS:
        installed = db_helper.query_one(
            "SELECT extension_install_id FROM oc_extension_install WHERE code = %s",
            (code,),
        )
        if not installed:
            ext = db_helper.query_one(
                "SELECT extension_id FROM oc_extension WHERE code = %s", (code,)
            )
            if not ext:
                logger.error(f"oc_extension 中不存在扩展: {code}，跳过")
                continue
            db_helper.execute(
                "INSERT IGNORE INTO oc_extension_install "
                "(extension_id, extension_download_id, name, description, code, "
                "version, author, link, status) "
                "VALUES (%s, 0, %s, %s, %s, '1.0', 'OpenCart', '', 1)",
                (
                    ext["extension_id"],
                    "Cash on Delivery" if code == "cod" else "Free Checkout",
                    "Cash on Delivery" if code == "cod" else "Free Checkout",
                    code,
                ),
            )
            logger.info(f"支付扩展已登记: {code}")

        for key, value in PAYMENT_SETTINGS.get(code, {}).items():
            if _insert_setting(f"payment_{code}", key, value):
                logger.info(f"支付设置已写入: {key} = {value}")

    # 自检：oc_extension_install 存在且 oc_setting 开关已开启
    problems = []
    for code in PAYMENTS:
        row = db_helper.query_one(
            "SELECT status FROM oc_extension_install WHERE code = %s", (code,)
        )
        status_setting = db_helper.query_one(
            "SELECT `value` FROM oc_setting WHERE code = %s AND `key` = %s",
            (f"payment_{code}", f"payment_{code}_status"),
        )
        if not row or row["status"] != 1:
            problems.append(f"{code}(oc_extension_install)")
        if not status_setting or status_setting["value"] != "1":
            problems.append(f"{code}(payment_{code}_status)")

    if problems:
        logger.error(f"自检失败，支付方式未完全启用: {problems}")
        return 1

    logger.info("支付方式自检通过: cod / free_checkout 均已启用")
    return 0


if __name__ == "__main__":
    sys.exit(main())
