import pytest
from pages.page_login import PageLogin
from utils.yaml_utils import read_yaml
import os
import allure

# 读取配置
config = read_yaml(os.path.join(os.path.dirname(__file__), '../config/config.yaml'))

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
        allure.dynamic.title(f"登录测试 - {case_name}")
        allure.dynamic.description(f"测试场景：{case_name}，期望提示：{case['expected']}")
        allure.dynamic.severity(allure.severity_level.CRITICAL)
        
        # 添加测试步骤
        with allure.step(f"输入用户名：{case['username']}"):
            pass
        with allure.step(f"输入密码：{'*' * len(case['password'])}"):
            pass
        with allure.step(f"输入验证码：{case.get('verify_code', '8888')}"):
            pass
        
        # 验证错误信息
        error_msg = self._execute_login(case)
        
        # 截图保存（根据你的记忆规范，测试通过需保留截图）
        with allure.step("截图保存"):
            screenshot = self.page_login.page_get_screenshot()
            if screenshot:
                allure.attach(
                    screenshot,
                    name="错误页面截图",
                    attachment_type=allure.attachment_type.PNG
                )
        
        print(f"错误信息：{error_msg}")
        assert case['expected'] in error_msg


    @allure.feature("登录功能")
    @allure.story("成功场景测试")
    @pytest.mark.smoke
    @pytest.mark.parametrize("case_name", [
        pytest.param("登录成功", id="login_success"),
    ])
    def test_login_success(self, case_name):
        """测试登录成功（冒烟测试）"""
        # 读取测试数据
        case = self._get_case_data(case_name, key="test_login_success")
        
        # Allure 动态标题
        allure.dynamic.title(f"登录测试 - {case_name}")
        allure.dynamic.description(f"测试场景：{case_name}，期望跳转至：{case['expected']}")
        allure.dynamic.severity(allure.severity_level.BLOCKER)
        
        # 添加测试步骤
        with allure.step(f"输入用户名：{case['username']}"):
            pass
        with allure.step(f"输入密码：{'*' * len(case['password'])}"):
            pass
        with allure.step(f"输入验证码：{case.get('verify_code', '8888')}"):
            pass
        
        # 执行登录
        with allure.step("执行登录操作"):
            self.page_login.page_login(
                case['username'],
                case['password'],
                case.get('verify_code', '8888')
            )
        
        # 验证登录成功：检查是否跳转到用户中心页面

        # 等待页面跳转完成（页面加载需要时间）
        import time
        time.sleep(3)  # 等待 3 秒确保页面完全加载
            
        current_url = self.driver.current_url
        with allure.step("验证登录结果"):
            print(f"登录后的 URL: {current_url}")
            print(f"期望的 URL: {case['expected']}")
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
