# -*- coding: utf-8 -*-
"""
播种固定测试账号 testuser_2026@example.com / Test@12345。

背景：测试套件中多个用例（API 登录态、UI 登录、数据库一致性）依赖该账号已存在。
本地环境靠历史数据累积，但 CI / 新环境是全新安装的 OpenCart，必须先播种。

实现：真实调用 OpenCart 注册接口（含 register_token CSRF 流程），幂等——
账号已存在（数据库可查到）时直接跳过。
用法：
    python scripts/seed_test_user.py
环境变量（可选）：UI_BASE_URL / DB_HOST / DB_USER / DB_PASSWORD / DB_DATABASE，见 config/config.ini.example
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests  # noqa: E402

from utils.config_reader import config  # noqa: E402
from utils.db_helper import db_helper  # noqa: E402
from utils.logger import logger  # noqa: E402

EMAIL = "testuser_2026@example.com"
PASSWORD = "Test@12345"
FIRSTNAME = "Test"
LASTNAME = "User"


def _user_exists(email: str) -> bool:
    """判断账号是否已在 oc_customer 落库"""
    row = db_helper.query_one(
        "SELECT customer_id FROM oc_customer WHERE email = %s", (email,)
    )
    return row is not None


def main() -> int:
    if _user_exists(EMAIL):
        logger.info(f"账号已存在，跳过播种: {EMAIL}")
        return 0

    base = config.get("ui", "base_url").rstrip("/")
    logger.info(f"站点地址: {base}")
    session = requests.Session()
    session.headers.update(
        {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json, text/html, */*",
        }
    )

    # 1) GET 注册页，获取 CSRF register_token
    try:
        page = session.get(f"{base}/index.php?route=account/register", timeout=20)
        page.raise_for_status()
    except Exception as e:
        logger.error(f"访问注册页失败: {e}")
        return 1
    logger.info(f"注册页 HTTP {page.status_code}，正文长度 {len(page.text)}")
    m = re.search(r"register_token=([a-zA-Z0-9]+)", page.text)
    if not m:
        # 输出页面片段辅助定位（页面结构或语言变化时）
        logger.error(
            f"注册页未找到 register_token，页面片段: {page.text[:500]}"
        )
        return 1
    token = m.group(1)

    # 2) 提交注册
    data = {
        "firstname": FIRSTNAME,
        "lastname": LASTNAME,
        "email": EMAIL,
        "telephone": "13800138000",
        "password": PASSWORD,
        "agree": "1",
    }
    register_url = f"{base}/index.php?route=account/register.register&register_token={token}"
    logger.info(f"POST 注册接口: {register_url}")
    response = session.post(
        register_url,
        data=data,
        allow_redirects=False,
        timeout=20,
    )
    logger.info(f"注册响应: status={response.status_code} ctype={response.headers.get('Content-Type')} body={response.text[:300]}")
    redirect = ""
    if response.headers.get("Content-Type", "").startswith("application/json"):
        redirect = json.loads(response.text).get("redirect", "")

    if "route=account/success" in redirect:
        logger.info(f"播种成功: {EMAIL}")
        return 0

    # 3) 若接口报错，以数据库为准兜底判断是否已存在
    if _user_exists(EMAIL):
        logger.info(f"接口未跳转成功页但账号已落库，视为已存在: {EMAIL}")
        return 0

    logger.error(f"播种失败，接口响应: status={response.status_code} body={response.text[:300]}")
    return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        import traceback

        traceback.print_exc()
        logger.error(f"播种脚本未捕获异常: {e}")
        sys.exit(1)
