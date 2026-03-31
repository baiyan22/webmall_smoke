from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
import os

# 清空代理环境变量
os.environ['HTTP_PROXY'] = ''
os.environ['HTTPS_PROXY'] = ''
os.environ['NO_PROXY'] = '*'


class DriverManager:
    """浏览器管理类 - 统一处理浏览器初始化和配置"""

    def __init__(self, config: dict):
        """
        初始化 DriverManager
        Args: config: 配置字典（从 YAML 读取）
        """
        self.config = config
        self.driver = None

    def create_driver(self):
        """
        根据配置创建浏览器对象
        Returns: WebDriver: 浏览器对象
        """
        # 如果 driver 已存在，直接返回（单例模式）
        if self.driver is not None:
            try:
                # 检查浏览器是否还存活
                _ = self.driver.current_url
                return self.driver
            except Exception:
                # 浏览器已关闭，重置
                self.driver = None

        browser_type = self.config.get('browser', 'chrome')

        if browser_type == 'chrome':
            options = webdriver.ChromeOptions()
            options.add_argument('--start-maximized')
            # 如果配置了驱动路径则使用，否则让 Selenium Manager 自动处理
            driver_path = self.config.get('chromedriver_path', '')
            if driver_path and os.path.exists(driver_path):
                service = ChromeService(executable_path=driver_path)
            else:
                service = ChromeService()  # Selenium Manager 会自动下载
            self.driver = webdriver.Chrome(service=service, options=options)
        elif browser_type == 'firefox':
            options = webdriver.FirefoxOptions()
            options.add_argument('--start-maximized')
            # 如果配置了驱动路径则使用，否则让 Selenium Manager 自动处理
            driver_path = self.config.get('geckodriver_path', '')
            if driver_path and os.path.exists(driver_path):
                service = FirefoxService(executable_path=driver_path)
            else:
                service = FirefoxService()  # Selenium Manager 会自动下载
            self.driver = webdriver.Firefox(service=service, options=options)
        else:
            raise ValueError(f"不支持的浏览器类型：{browser_type}")

        # 设置隐式等待
        self.driver.implicitly_wait(self.config.get('implicit_wait', 10))
        return self.driver

    def get_driver(self):
        """
        获取当前的浏览器对象
        Returns: WebDriver: 浏览器对象
        Raises: RuntimeError: 如果 driver 尚未创建
        """
        if self.driver is None:
            raise RuntimeError("浏览器尚未创建，请先调用 create_driver()")
        return self.driver

    def quit_driver(self):
        """关闭浏览器并重置 driver"""
        if self.driver is not None:
            try:
                self.driver.quit()
            except Exception as e:
                print(f"关闭浏览器时出错：{e}")
            finally:
                self.driver = None
