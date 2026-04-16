import pytest
from utils.yaml_utils import read_yaml
from drivers.driver_manager import DriverManager
from utils.log_utils import GetLogger
import os
import shutil
from datetime import datetime

# 日志实例化
logger = GetLogger().get_logger()

# 读取配置
config = read_yaml(os.path.join(os.path.dirname(__file__), 'config/config.yaml'))


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook: 监听测试用例执行状态，失败时自动截图并附加到 Allure 报告
    
    工作流程:
    1. 执行测试用例
    2. 检查用例是否失败
    3. 如果失败，自动截图并保存到 temps 目录
    4. 将截图附加到 Allure 报告中
    """
    # 执行测试用例并获取结果
    outcome = yield
    rep = outcome.get_result()
    
    # 只处理失败的测试用例（跳过 setup/teardown 阶段）
    if rep.when == "call" and rep.failed:
        try:
            # 获取 driver 实例
            driver = item.funcargs.get("driver")
            if driver:
                # 生成截图文件名（包含时间戳和用例名）
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                test_name = item.name
                screenshot_filename = f"{timestamp}_{test_name}_failed.png"
                screenshot_path = os.path.join(
                    os.path.dirname(__file__), 
                    "image",
                    screenshot_filename
                )
                
                # 确保 temps 目录存在
                os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
                
                # 截图并保存
                driver.save_screenshot(screenshot_path)
                logger.warning(f"⚠️  测试失败，已自动截图: {screenshot_filename}")
                
                # 将截图附加到 Allure 报告
                import allure
                with open(screenshot_path, "rb") as f:
                    allure.attach(
                        f.read(),
                        name=f"失败截图 - {test_name}",
                        attachment_type=allure.attachment_type.PNG
                    )
        except Exception as e:
            logger.error(f"❌ 自动截图失败: {str(e)}")


@pytest.fixture(scope="session", autouse=True)
def clean_test_artifacts():
    """
    Fixture: 测试会话开始前清理旧的测试产物
    
    清理内容:
    - 清空 temps 目录下的旧截图
    - 清空 logs 目录下的旧日志文件
    - 清空 report 目录（避免与上次报告混淆）
    """
    logger.info(" 开始清理旧的测试产物...")
    
    # 定义需要清理的目录
    dirs_to_clean = [
        os.path.join(os.path.dirname(__file__), "temps"),
        os.path.join(os.path.dirname(__file__), "logs"),
        os.path.join(os.path.dirname(__file__), "report"),
    ]
    
    for dir_path in dirs_to_clean:
        if os.path.exists(dir_path):
            try:
                # 遍历目录中的所有文件并删除
                for filename in os.listdir(dir_path):
                    file_path = os.path.join(dir_path, filename)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                logger.info(f"✓ 已清空目录: {dir_path}")
            except Exception as e:
                logger.warning(f"⚠  清理目录 {dir_path} 失败: {str(e)}")
        else:
            logger.debug(f"目录不存在，跳过清理: {dir_path}")
    
    logger.info(" 测试产物清理完成")
    yield
    logger.info(" 测试会话结束")


@pytest.fixture(scope="session")
def driver():
    """pytest fixture: 创建并返回浏览器对象"""
    logger.info("="*50)
    logger.info("开始初始化测试环境")
    
    # 创建 DriverManager 实例
    driver_manager = DriverManager(config)

    # 创建浏览器对象
    logger.info(f"创建浏览器: {config.get('browser', 'chrome')}")
    driver = driver_manager.create_driver()

    #最大化浏览器
    driver.maximize_window()
    logger.debug("浏览器窗口已最大化")

    # 访问指定 URL
    logger.info(f"访问目标 URL: {config['url']}")
    driver.get(config['url'])
    logger.info("测试环境初始化完成")
    logger.info("="*50)

    yield driver

    # 测试结束后关闭浏览器
    logger.info("测试结束，关闭浏览器")
    driver_manager.quit_driver()


@pytest.fixture(scope="function")
def no_login(driver):
    """
    未登录状态的 fixture
    用于测试登录、注册等不需要登录的页面
    """
    logger.debug("Fixture [no_login] 开始 - 返回首页确保初始状态")
    # 重新访问首页，确保每次测试都从初始状态开始
    driver.get(config['url'])
    logger.debug("Fixture [no_login] 准备就绪")
    yield driver
    logger.debug("Fixture [no_login] 结束")


@pytest.fixture(scope="function")
def logged_in(driver):
    """
    已登录状态的 fixture
    用于测试搜索、下单等需要登录的业务功能
    
    智能策略：
    - 如果浏览器已有登录状态（冒烟测试串联时）→ 直接使用
    - 如果浏览器未登录（单独运行搜索测试时）→ 执行登录
    """
    from pages.page_login import PageLogin
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    
    logger.info("Fixture [logged_in] 开始 - 检查登录状态")
    
    # 从配置读取登录账号
    test_account = config.get('test_account', {}) or {}
    username = test_account.get('username')
    password = test_account.get('password')
    verify_code = test_account.get('verify_code', '8888')
    
    # 检查是否已经登录（通过检查是否有退出登录链接）
    is_logged_in = False
    try:
        # 等待 3 秒查找“退出”链接
        logout_link = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "退出"))
        )
        if logout_link.is_displayed():
            logger.info(f"✓ 检测到已登录状态（用户：{username}），跳过登录步骤")
            is_logged_in = True
    except:
        is_logged_in = False
        logger.info("⚠ 未检测到登录状态，准备执行登录...")
    
    # 如果未登录，则执行登录操作
    if not is_logged_in:
        try:
            logger.info("开始执行登录操作")
            # 访问首页
            driver.get(config['url'])
            
            # 等待登录链接可点击
            login_link = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "登录"))
            )
            
            # 执行登录操作
            login_page = PageLogin(driver)
            login_page.page_login(username, password, verify_code)
            
            # 等待登录完成和页面跳转
            import time
            time.sleep(2)
            
            logger.info(f"✓ 登录成功（用户：{username}）")
        except Exception as e:
            logger.error(f"❌ 登录失败：{str(e)}")
            # 截图保存现场
            import allure
            screenshot = driver.get_screenshot_as_png()
            allure.attach(
                screenshot,
                name="登录失败截图",
                attachment_type=allure.attachment_type.PNG
            )
            raise
    
    logger.info("Fixture [logged_in] 准备就绪")
    yield driver
    
    # 测试完成后不退出登录，保持会话给后续测试使用
    logger.debug("Fixture [logged_in] 结束")
