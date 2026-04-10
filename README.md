# 电商网站自动化测试框架

基于 **POM (Page Object Model)** 设计模式的 UI 自动化测试框架，使用 Python + Selenium + Pytest 构建，实现电商网站的核心冒烟测试。

##  项目简介

本项目是一个典型的 Web UI 自动化测试框架，采用 POM 设计模式，将页面定位与业务逻辑分离，提高代码的可维护性和复用性。目前实现了电商网站的核心冒烟测试流程，包括注册、登录、搜索、商品详情和购物车功能。

##  技术栈

- **编程语言**: Python
- **测试框架**: Pytest
- **浏览器自动化**: Selenium WebDriver
- **驱动管理**: webdriver-manager
- **数据管理**: PyYAML
- **测试报告**: Allure Report
- **并行执行**: pytest-xdist
- **用例排序**: pytest-ordering

##  项目结构

```
PO_model/
├── base/                    # 基础层
│   └── base_page.py        # 页面基类，封装通用操作
├── config/                  # 配置层
│   └── config.yaml         # 全局配置文件（URL、浏览器、账号等）
├── drivers/                 # 驱动层
│   └── driver_manager.py   # 浏览器驱动管理器
├── locators/                # 定位层
│   └── cart_page_locators.yaml
├── pages/                   # 页面对象层（POM 核心）
│   ├── page_cart.py        # 购物车页面对象
│   ├── page_good_detail.py # 商品详情页面对象
│   ├── page_login.py       # 登录页面对象
│   ├── page_register.py    # 注册页面对象
│   └── page_search.py      # 搜索页面对象
├── test_cases/              # 测试用例层
│   ├── test_01_register.py # 注册测试
│   ├── test_02_login.py    # 登录测试
│   ├── test_03_search.py   # 搜索测试
│   ├── test_04_good_detail.py  # 商品详情测试
│   └── test_05_cart.py     # 购物车测试
├── test_data/               # 测试数据层
│   ├── cart_data.yaml
│   ├── good_detail_data.yaml
│   ├── login_data.yaml
│   ├── register_data.yaml
│   └── search_data.yaml
├── utils/                   # 工具层
│   ├── locator_manager.py  # 定位器管理
│   ├── log_utils.py        # 日志工具
│   └── yaml_utils.py       # YAML 读取工具
├── temps/                   # Allure 临时数据目录
├── report/                  # Allure 测试报告目录
├── conftest.py             # Pytest 夹具配置
├── pytest.ini              # Pytest 配置文件
└── requirements.txt        # 项目依赖
```

## ✅ 已实现的测试用例

### 1. 注册功能 (test_01_register.py)
- ✅ 注册成功（冒烟测试）
- ✅ 异常场景测试：
  - 手机格式错误
  - 邮箱格式错误
  - 密码格式错误（位数）
  - 密码格式错误（有空格）
  - 密码不一致
  - 服务协议未勾选
  - 验证码错误
  - 用户名已存在

### 2. 登录功能 (test_02_login.py)
- ✅ 登录成功（冒烟测试）
- ✅ 异常场景测试：
  - 密码错误
  - 验证码错误
  - 用户不存在

### 3. 搜索功能 (test_03_search.py)
- ✅ 搜索功能正常（冒烟测试）

### 4. 商品详情功能 (test_04_good_detail.py)
- ✅ 商品详情查看（冒烟测试）

### 5. 购物车功能 (test_05_cart.py)
- ✅ 加入购物车成功（冒烟测试）
- ✅ 购物车价格计算验证

## 环境准备

### 前置要求
- Python 3.8+
- Chrome 浏览器（或其他主流浏览器）
- 稳定的网络连接（用于下载驱动和访问测试网站）

### 安装步骤

1. **克隆项目**
```bash
git clone <your-repo-url>
cd PO_model
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置浏览器驱动**
   
   项目使用 `webdriver-manager` 自动管理驱动，但也可以手动配置：
   
   - 编辑 `config/config.yaml`
   - 修改 `chromedriver_path` 为你的实际路径

4. **配置测试环境**
   
   编辑 `config/config.yaml`：
```yaml
# 前端服务器地址
url: "https://hmshop-test.itheima.net/"

# 浏览器配置
browser: "chrome"  # 可选：chrome, firefox, edge

# 测试账号配置
test_account:
  username: "13333333338"
  password: "123456"
  verify_code: "8888"
```

## ▶ 运行测试

### 运行所有测试
```bash
pytest
```

### 只运行冒烟测试
```bash
pytest -m smoke
```

### 运行指定测试文件
```bash
pytest test_cases/test_01_register.py -v
```

### 运行指定测试用例
```bash
pytest test_cases/test_01_register.py::TestRegister::test_register_success -v
```

### 并行执行测试
```bash
pytest -n 4  # 使用 4 个进程并行执行
```

### 生成 HTML 报告
```bash
pytest --html=report/report.html
```

### 生成 Allure 报告
```bash
# 执行测试并生成 allure 数据
pytest --alluredir=./temps --clean-alluredir

# 生成报告
allure generate ./temps -o ./report -c

# 查看报告
allure open ./report
```

##  测试报告示例

执行测试后会自动生成 Allure 测试报告，包含：
- 测试概览（通过率、用例分布）
- 详细的测试步骤和截图
- 失败用例的错误信息
- 历史趋势分析

## 🔧 自定义配置

### 添加新的测试用例
1. 在 `test_data/` 对应的 YAML 文件中添加测试数据
2. 在 `test_cases/` 对应的测试文件中编写测试方法
3. 使用 `@pytest.mark.smoke` 标记冒烟测试用例

### 添加新的页面对象
1. 在 `locators/` 创建新的定位器 YAML 文件
2. 在 `pages/` 创建新的页面对象类
3. 继承 `base/base_page.py` 中的基类

### 修改日志配置
编辑 `utils/log_utils.py` 调整日志级别和输出格式

## 📝 测试策略

### 冒烟测试 (Smoke Test)
- 只测试核心业务流程
- 确保主要功能正常工作
- 快速验证系统稳定性
- 标记为 `@pytest.mark.smoke`


### 数据驱动测试
- 测试数据与代码分离
- 使用 YAML 管理测试数据
- 支持批量添加测试场景

