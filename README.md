# auto_test_framework - OpenCart 电商自动化测试框架

针对 OpenCart 4.1.0.3 电商系统的全链路自动化测试框架：UI 自动化（Playwright）+ API 测试（Requests）+ 数据库数据一致性验证（PyMySQL），带 GitHub Actions 持续集成（云端自动部署被测环境）与 Allure 报告。

## 技术栈

- **Python 3.10+** · **Pytest** · **Playwright**(UI) · **Requests**(API) · **Allure**(报告) · **PyMySQL**(DB)
- **被测系统**:OpenCart 4.1.0.3 + MySQL 8.0(库 `xiangmu`,表前缀 `oc_`)

## 目录结构

```
auto_test_framework/
├── config/config.ini.example   # 配置模板（真实 config.ini 不入库，见下方"配置"）
├── data/                       # users.json / products.json 测试数据
├── utils/                      # config_reader / logger / api_client / db_helper
├── pages/                      # POM 页面对象（base/login/register/product/checkout）
├── tests/
│   ├── test_ui/                # UI 测试：登录/注册/搜索/购物车/结算/完整下单流程
│   ├── test_api/               # API 测试：直接请求 OpenCart 路由接口
│   └── test_db/                # 数据一致性测试
├── scripts/
│   ├── seed_test_user.py       # 播种固定测试账号（幂等）
│   └── enable_payment_extensions.py  # 启用支付方式并准备结算前置（幂等）
├── setup.py                    # 本地一键初始化（建库/装依赖/装 Playwright）
├── .github/workflows/test.yml  # GitHub Actions：云端自建 OpenCart 后跑全部测试
├── conftest.py / pytest.ini / requirements.txt
└── docs/                       # 测试计划 / 用例 / 缺陷报告 / 测试报告
```

> 注意：**被测系统 OpenCart 不包含在本仓库**。测试需要一个已部署的 OpenCart 站点 + MySQL。CI 会在云端自动完成部署；本地运行需自备环境（见下文）。

## 如何运行

### 方式一：GitHub Actions（推荐，无需任何本地环境）

仓库已配置 `.github/workflows/test.yml`：云端每次会自动 **下载 OpenCart 4.1.0.3 → 安装（含演示数据）→ 启用支付 → 播种测试账号 → 运行全部测试 → 上传 Allure 报告**，也会在每日 02:00 定时回归。

想在自己账号下复现：

1. Fork（或复制）本仓库到你自己的 GitHub
2. 推送一次代码（`git push`）触发 CI
3. 在 **Actions** 页查看运行结果与日志
4. 运行完成后，在 run 页面下载 **test-report** artifact（Allure 结果），或本地执行 `allure serve` 查看报告

CI 运行无需配置任何 Secrets；仅在你想收到**邮件通知**时，在仓库 `Settings → Secrets and variables → Actions` 配置：

- `SMTP_USERNAME`：QQ 邮箱地址（发件与收件均为它）
- `SMTP_PASSWORD`：QQ 邮箱的 **SMTP 授权码**（在 QQ 邮箱 设置→账户 中开启 SMTP 后生成，非登录密码）

未配置时邮件步骤自动跳过，不影响测试结果。

### 方式二：本地运行（需要自备被测环境）

测试需要一个能访问的 OpenCart 4.x（含演示数据）与 MySQL。任选其一部署被测系统：

- 有 Docker：用官方 [opencart/opencart](https://github.com/opencart/opencart) 镜像或参考 `.github/workflows/test.yml` 中的部署步骤
- 无 Docker：安装 MySQL，下载 [OpenCart 4.1.0.3](https://github.com/opencart/opencart/releases) 的 `upload` 到站点目录，运行 `php install/cli_install.php install ...`（参数见 workflow 第 4 步），再执行本仓库的 `scripts/enable_payment_extensions.py`

环境就绪后：

```bash
# 1) 安装依赖（含 Playwright Chromium）
python -m venv venv && source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install chromium

# 2) 准备配置：从模板复制，或用环境变量注入（推荐 CI 方式）
cp config/config.ini.example config/config.ini      # 填入本地数据库密码
#   或 export DB_HOST=... DB_USER=root DB_PASSWORD=... DB_DATABASE=xiangmu UI_BASE_URL=http://localhost/opencart/

# 3) 播种测试数据（固定账号 testuser_2026@example.com）
python scripts/enable_payment_extensions.py
python scripts/seed_test_user.py

# 4) 运行测试（顺序：UI 下单在前，DB 一致性验证在后）
python -m pytest tests/test_ui/ tests/test_api/ tests/test_db/

# 5) 查看 Allure 报告
allure serve allure-results
```

## 配置说明（utils/config_reader.py）

读取优先级：**环境变量 > config/config.ini > config/config.ini.example**

- 环境变量键 = `[section]_[key]` 大写，如 `DB_PASSWORD`、`UI_BASE_URL`
- `config/config.ini` 含真实密码，已被 `.gitignore` 忽略，不会提交
- 仓库只维护 `config/config.ini.example` 模板

## 测试设计

- 流程：注册用户 → 登录 → 搜索商品 → 加购物车 → 下单结算 → 数据库验证订单落库
- **UI 端到端**(test_checkout_flow.py)：真实走 OpenCart 4 结算（填配送地址 → 选配送/支付方式 → 确认订单），并在 `oc_order` 验证订单真实落库
- **API 层**：requests 直接调用 OpenCart 路由接口，断言含业务结果（注册成功跳转+落库、登录可访问账户页、加购后购物车含商品等）
- **数据一致性**：注册/订单/订单商品/库存校验
- 缺陷 BUG-002（未登录访问结算页重定向到购物车页而非登录页）以 `xfail` 标记为已知缺陷，修复后会自动 XPASS 提醒

## 文档

测试计划、用例、缺陷报告、测试报告见 `docs/`。
