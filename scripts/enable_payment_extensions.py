# -*- coding: utf-8 -*-
"""
启用 OpenCart 内置支付方式（cod / free_checkout）。

背景：OpenCart 演示数据（install/opencart-en-gb.sql）只注册扩展
（oc_extension），oc_extension_install 为空表，结算页没有任何可用
支付方式，导致无法下单。本地环境曾由 setup.py 手工补过，CI / 新环境
需在执行测试前调用本脚本。幂等：已安装则跳过。
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


def main() -> int:
    for code in PAYMENTS:
        installed = db_helper.query_one(
            "SELECT extension_install_id FROM oc_extension_install WHERE code = %s",
            (code,),
        )
        if installed:
            logger.info(f"支付方式已安装，跳过: {code}")
            continue

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
        logger.info(f"支付方式已启用: {code}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
