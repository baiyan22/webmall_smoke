import pytest
from pages.page_login import PageLogin
from utils.yaml_utils import read_yaml
from utils.log_utils import GetLogger
import os
import allure

# 读取配置
config = read_yaml(os.path.join(os.path.dirname(__file__), '../config/config.yaml'))

# 日志实例化
logger = GetLogger().get_logger()

test_data = read_yaml(os.path.join(os.path.dirname(__file__), '../test_data/login_data.yaml'))

class TestLogin:
    """登录功能测试类"""
    
    # 类属性声明（避免使用 __init__ 影响 pytest 收集）
    driver = None
    page_login = None

    @pytest.fixture(autouse=True)
    def setup(self, no_login):
        """每个测试前初始化登录页面对象并返回首页"""
        self.driver = no_login
        self.page_login = PageLogin(no_login)

    # 获取测试数据
    def _get_case_data(self, case_name, key):
        """
        根据用例名称获取测试数据
        Args: 
            case_name: 用例名称
            key: YAML 中的 key对象，用于分别成功、失败场景
        Returns: dict: 测试数据
        """
        # 根据类型选择对应的数据列表
        if key == "test_login_fail":
            data_list = test_data['test_login_fail']
        else:
            data_list = test_data['test_login_success']
            
        for case in data_list:
            if case['name'] == case_name:
                return case
        raise ValueError(f"未找到测试用例：{case_name}")

    def _execute_login(self, case):
        """
        执行登录流程并获取错误信息
        Args: case: 测试用例数据
        Returns: str: 错误信息
        """
        # 执行登录
        self.page_login.page_login(
            case['username'],
            case['password'],
            case.get('verify_code', '8888')
        )

        # 获取错误信息
        error_msg = self.page_login.page_get_err_info()

        return  error_msg


    @allure.feature("登录功能")
    @allure.story("异常场景测试")
    @pytest.mark.parametrize("case_name", [
        pytest.param("密码错误", id="wrong_password"),
        pytest.param("验证码错误", id="wrong_verify_code"),
        pytest.param("用户不存在", id="user_not_exist"),
    ])
    def test_login_failures(self, case_name):
        """测试登录失败场景（异常测试）"""
        # 读取测试数据
        case = self._get_case_data(case_name, key="test_login_fail")
        
        # Allure 动态标题
        allure.dynamic.title(f"⚠️ 登录功能 - {case_name}")
        allure.dynamic.description(
            f"**测试场景**: {case_name}\n\n"
            f"**测试目标**:\n"
            f"- 验证登录失败时的错误提示\n"
            f"- 确保系统不会崩溃\n\n"
            f"**期望提示**: {case['expected']}"
        )
        allure.dynamic.severity(allure.severity_level.CRITICAL)
        allure.dynamic.tag("exception", "login")
        
        # 添加测试数据附件
        with allure.step("📋 测试数据"):
            allure.attach(
                f"用户名: {case['username']}\n"
                f"密码: {'*' * len(case['password'])}\n"
                f"验证码: {case.get('verify_code', '8888')}",
                name="测试数据详情",
                attachment_type=allure.attachment_type.TEXT
            )
        
        # 验证错误信息
        error_msg = self._execute_login(case)
        
        logger.info(f"错误信息：{error_msg}")
        
        # 截图保存（根据你的记忆规范，测试通过需保留截图）
        with allure.step("📸 截图保存"):
            screenshot = self.page_login.page_get_screenshot()
            if screenshot:
                allure.attach(
                    screenshot,
                    name="登录错误页面截图",
                    attachment_type=allure.attachment_type.PNG
                )
        
        assert case['expected'] in error_msg
        logger.info(f"✓ 登录异常测试通过: {case_name}")


    @allure.feature("登录功能")
    @allure.story("成功场景测试")
    @pytest.mark.smoke
    @pytest.mark.parametrize("case_name", [
        pytest.param("登录成功", id="login_success"),
    ])
    def test_login_success(self, case_name):
        """测试登录成功"""
        # 读取测试数据
        case = self._get_case_data(case_name, key="test_login_success")
        
        # Allure 动态标题
        allure.dynamic.title(f"✅ 登录功能 - {case_name}（冒烟测试）")
        allure.dynamic.description(
            f"**测试场景**: {case_name}\n\n"
            f"**测试目标**:\n"
            f"- 验证正常登录流程\n"
            f"- 验证登录后跳转\n"
            f"- 验证用户会话创建成功\n\n"
            f"**用户名**: {case['username']}\n"
            f"**预期结果**: 登录成功，跳转到用户中心"
        )
        allure.dynamic.severity(allure.severity_level.BLOCKER)
        allure.dynamic.tag("smoke", "login", "success")
        
        # 添加测试数据附件
        with allure.step("📋 测试数据"):
            allure.attach(
                f"用户名: {case['username']}\n"
                f"密码: {'*' * len(case['password'])}\n"
                f"验证码: {case.get('verify_code', '8888')}",
                name="测试数据详情",
                attachment_type=allure.attachment_type.TEXT
            )
        
        # 执行登录
        with allure.step("🔄 执行登录操作"):
            logger.info("开始执行登录流程")
            self.page_login.page_login(
                case['username'],
                case['password'],
                case.get('verify_code', '8888')
            )
            logger.info("登录流程执行完成")
        
        # 验证登录成功：检查是否跳转到用户中心页面

        # 等待页面跳转完成（页面加载需要时间）
        import time
        time.sleep(3)  # 等待 3 秒确保页面完全加载
            
        current_url = self.driver.current_url
        with allure.step("✅ 验证登录结果"):
            logger.info(f"登录后的 URL: {current_url}")
            logger.info(f"期望的 URL: {case['expected']}")
            # 附加页面截图
            screenshot = self.page_login.page_get_screenshot()
            if screenshot:
                allure.attach(
                    screenshot,
                    name="登录成功页面截图",
                    attachment_type=allure.attachment_type.PNG
                )
        
        # 验证是否跳转到用户中心页面
        assert current_url == case['expected'], f"登录失败，当前 URL: {current_url}, 期望 URL: {case['expected']}"
        logger.info("✓ 登录成功测试通过")
