from selenium.webdriver.common.by import By
from base.base_page import BasePage
from utils.log_utils import GetLogger

logger = GetLogger().get_logger()

#登录页面类
class PageLogin(BasePage):
    """登录页面数据配置"""
    # 登录链接
    login_link = By.PARTIAL_LINK_TEXT, "登录"

    # 用户名（手机号/邮箱）
    login_username = By.ID, "username"

    # 密码
    login_pwd = By.ID, "password"

    # 验证码
    login_verify_code = By.ID, "verify_code"

    # 登录按钮
    login_btn = By.CSS_SELECTOR, ".J-login-submit"
    
    # 获取异常文本信息
    login_err_info = By.CSS_SELECTOR, ".layui-layer-content"

    # 点击异常提示框按钮
    login_err_info_btn = By.CSS_SELECTOR, ".layui-layer-btn0"

    # 退出登录
    logout_link = By.PARTIAL_LINK_TEXT, "退出"

    def __init__(self, driver):
        super().__init__(driver)  # 调用父类构造函数

    #点击登录链接
    def page_click_login_link(self):
        logger.info("点击登录链接")
        self.base_click(self.login_link)

    #输入用户名
    def page_input_username(self,username):
        logger.info(f"输入用户名: {username}")
        self.base_input(self.login_username,username)

    #输入密码
    def page_input_pwd(self,pwd):
        logger.debug("输入密码")
        self.base_input(self.login_pwd,pwd)

    #输入验证码
    def page_input_code(self,code):
        logger.debug(f"输入验证码: {code}")
        self.base_input(self.login_verify_code, code)

    #点击登录按钮
    def page_click_login_btn(self):
        logger.info("点击登录按钮")
        self.base_click(self.login_btn)

    #获取异常信息
    def page_get_err_info(self):
        """获取错误提示信息（带等待）"""
        import time
        logger.debug("等待并获取错误提示信息")
        time.sleep(1)  # 等待提示框出现
        try:
            error_text = self.base_get_text(self.login_err_info)
            logger.info(f"获取到错误信息: {error_text}")
            return error_text
        except:
            logger.warning("未找到错误提示元素")
            return None

    #点击异常信息按钮
    def page_click_err_info_btn(self):
        self.base_click(self.login_err_info_btn)

    #截图
    def page_get_screenshot(self):
        self.base_get_screenshot()

    #退出登录
    def page_logout(self):
        self.base_click(self.logout_link)

    #组合业务信息
    def page_login(self,username,pwd,code=None):
        logger.info("="*30 + " 开始执行登录流程 " + "="*30)
        self.page_click_login_link()
        self.page_input_username(username)
        self.page_input_pwd(pwd)
        self.page_input_code(code)
        self.page_click_login_btn()
        logger.info("="*30 + " 登录流程执行完成 " + "="*30)