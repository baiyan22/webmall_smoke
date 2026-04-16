from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from utils.log_utils import GetLogger
import os

# 日志实例化
logger = GetLogger().get_logger()

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
                logger.debug("复用已存在的浏览器实例")
                return self.driver
            except Exception:
                # 浏览器已关闭，重置
                logger.warning("检测到浏览器已关闭，重新创建")
                self.driver = None

        browser_type = self.config.get('browser', 'chrome')
        logger.info(f"正在创建 {browser_type} 浏览器...")

        if browser_type == 'chrome':
            options = webdriver.ChromeOptions()
            options.add_argument('--start-maximized')
            # 使用 Selenium 4 内置的 Selenium Manager 自动管理 ChromeDriver
            logger.debug("使用 Selenium Manager 自动管理 ChromeDriver")
            service = ChromeService()  # Selenium Manager 会自动检测浏览器版本并下载匹配的驱动
            self.driver = webdriver.Chrome(service=service, options=options)
            logger.info("Chrome 浏览器创建成功")
        elif browser_type == 'firefox':
            options = webdriver.FirefoxOptions()
            options.add_argument('--start-maximized')
            # 使用 Selenium 4 内置的 Selenium Manager 自动管理 GeckoDriver
            logger.debug("使用 Selenium Manager 自动管理 GeckoDriver")
            service = FirefoxService()  # Selenium Manager 会自动检测浏览器版本并下载匹配的驱动
            self.driver = webdriver.Firefox(service=service, options=options)
            logger.info("Firefox 浏览器创建成功")
        else:
            logger.error(f"不支持的浏览器类型：{browser_type}")
            raise ValueError(f"不支持的浏览器类型：{browser_type}")

        # 设置隐式等待
        implicit_wait = self.config.get('implicit_wait', 10)
        self.driver.implicitly_wait(implicit_wait)
        logger.debug(f"设置隐式等待时间: {implicit_wait}s")
        
        logger.info("浏览器初始化完成")
        return self.driver

    def get_driver(self):
        """
        获取当前的浏览器对象
        Returns: WebDriver: 浏览器对象
        Raises: RuntimeError: 如果 driver 尚未创建
        """
        if self.driver is None:
            logger.error("浏览器尚未创建，请先调用 create_driver()")
            raise RuntimeError("浏览器尚未创建，请先调用 create_driver()")
        logger.debug("获取浏览器实例")
        return self.driver

    def quit_driver(self):
        """关闭浏览器并重置 driver"""
        if self.driver is not None:
            try:
                logger.info("正在关闭浏览器...")
                self.driver.quit()
                logger.info("浏览器已关闭")
            except Exception as e:
                logger.error(f"关闭浏览器时出错：{e}")
            finally:
                self.driver = None
                logger.debug("Driver 实例已重置")
