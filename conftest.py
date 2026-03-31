import pytest
from utils.yaml_utils import read_yaml
from drivers.driver_manager import DriverManager
import os

# 读取配置
config = read_yaml(os.path.join(os.path.dirname(__file__), 'config/config.yaml'))


@pytest.fixture(scope="session")
def driver():
    """pytest fixture: 创建并返回浏览器对象"""
    # 创建 DriverManager 实例
    driver_manager = DriverManager(config)

    # 创建浏览器对象
    driver = driver_manager.create_driver()

    #最大化浏览器
    driver.maximize_window()

    # 访问指定 URL
    driver.get(config['url'])

    yield driver

    # 测试结束后关闭浏览器
    driver_manager.quit_driver()


@pytest.fixture(scope="function")
def no_login(driver):
    """
    未登录状态的 fixture
    用于测试登录、注册等不需要登录的页面
    """
    # 重新访问首页，确保每次测试都从初始状态开始
    driver.get(config['url'])
    yield driver


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
    
    # 从配置读取登录账号
    test_account = config.get('test_account', {}) or {}
    username = test_account.get('username')
    password = test_account.get('password')
    verify_code = test_account.get('verify_code', '8888')
    
    # 检查是否已经登录（通过检查是否有退出登录链接）
    is_logged_in = False
    try:
        # 等待 3 秒查找"退出"链接
        logout_link = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "退出"))
        )
        if logout_link.is_displayed():
            print(f"✓ 检测到已登录状态（用户：{username}），跳过登录步骤")
    except:
        is_logged_in = False
        print("⚠ 未检测到登录状态，准备执行登录...")
    
    # 如果未登录，则执行登录操作
    if not is_logged_in:
        try:
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
            
            print(f"✓ 登录成功（用户：{username}）")
        except Exception as e:
            print(f"❌ 登录失败：{str(e)}")
            # 截图保存现场
            import allure
            screenshot = driver.get_screenshot_as_png()
            allure.attach(
                screenshot,
                name="登录失败截图",
                attachment_type=allure.attachment_type.PNG
            )
            raise
    
    yield driver
    
    # 测试完成后不退出登录，保持会话给后续测试使用
