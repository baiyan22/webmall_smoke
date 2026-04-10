import pytest
from utils.yaml_utils import read_yaml
from drivers.driver_manager import DriverManager
from utils.log_utils import GetLogger
import os

# 日志实例化
logger = GetLogger().get_logger()

# 读取配置
config = read_yaml(os.path.join(os.path.dirname(__file__), 'config/config.yaml'))


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
