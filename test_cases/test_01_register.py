import pytest
from utils.log_utils import GetLogger
from pages.page_register import PageRegister
from utils.yaml_utils import read_yaml
import os
import allure

# 读取配置
config = read_yaml(os.path.join(os.path.dirname(__file__), '../config/config.yaml'))

# 读取测试数据
test_data = read_yaml(os.path.join(os.path.dirname(__file__), '../test_data/register_data.yaml'))

# 日志实例化
logger = GetLogger().get_logger()

class TestRegister:
    """注册功能测试类"""
    
    # 类属性声明（避免使用 __init__ 影响 pytest 收集）
    driver = None
    page_register = None

    @pytest.fixture(autouse=True)
    def setup(self, no_login):
        """每个测试前初始化注册页面对象并返回首页"""
        self.driver = no_login
        self.page_register = PageRegister(no_login)

    #获取测试数据
    def _get_case_data(self, case_name, key="test_register_success"):
        """
        根据用例名称获取测试数据
        Args: 
            case_name: 用例名称
            key: YAML 中的 key，默认从成功场景读取
        Returns: dict: 测试数据
        """
        # 根据类型选择对应的数据列表
        if key == "test_register_fail":
            data_list = test_data['test_register_fail']
        else:
            data_list = test_data['test_register_success']
            
        for case in data_list:
            if case['name'] == case_name:
                return case
        raise ValueError(f"未找到测试用例：{case_name}")
    
    def _execute_register(self, case):
        """
        执行注册流程并获取错误信息
        Args: case: 测试用例数据
        Returns: str: 错误信息
        """
        # 执行注册
        self.page_register.page_register(
            register_way=case['register_way'],
            username=case['username'],
            pwd=case['password'],
            confirm_pwd=case['confirm_pwd'],
            code=case['verify_code'],
            check_protocol=case.get('check_protocol', True)
        )
        
        # 获取错误信息
        error_msg = self.page_register.page_get_err_info()
        print(f"错误信息：{error_msg}")

        
        return error_msg


    @allure.feature("注册功能")
    @allure.story("异常场景测试")
    @pytest.mark.parametrize("case_name", [
        pytest.param("手机格式错误", id="wrong_phone_format"),
        pytest.param("邮箱格式错误", id="wrong_email_format"),
        pytest.param("密码格式错误 (位数)", id="wrong_password_length"),
        pytest.param("密码格式错误 (有空格)", id="wrong_password_space"),
        pytest.param("密码不一致", id="password_mismatch"),
        pytest.param("服务协议未勾选", id="protocol_not_checked"),
        pytest.param("验证码错误", id="wrong_verify_code"),
        pytest.param("用户名已存在", id="username_exists"),
    ])
    def test_register_failures(self, case_name):
        """测试注册失败场景（异常测试）"""
        logger.info(f"开始执行测试：{case_name}")
        case = self._get_case_data(case_name, key="test_register_fail")
        
        # Allure 动态标题和描述
        allure.dynamic.title(f"注册测试 - {case_name}")
        allure.dynamic.description(
            f"测试场景：{case_name}\n"
            f"注册方式：{case['register_way']}\n"
            f"期望提示：{case['expected']}"
        )
        allure.dynamic.severity(allure.severity_level.CRITICAL)
        
        # 添加测试步骤
        with allure.step(f"注册方式：{case['register_way']}"):
            pass
        with allure.step(f"用户名：{case['username']}"):
            pass
        with allure.step(f"密码：{'*' * len(case['password'])}"):
            pass
        with allure.step(f"确认密码：{'*' * len(case['confirm_pwd'])}"):
            pass
        with allure.step(f"验证码：{case['verify_code']}"):
            pass
        if 'check_protocol' in case:
            with allure.step(f"是否勾选协议：{case['check_protocol']}"):
                pass
        
        # 执行注册并获取错误信息
        error_msg = self._execute_register(case)
        
        # 截图保存
        with allure.step("截图保存"):
            screenshot = self.page_register.page_get_screenshot()
            if screenshot:
                allure.attach(
                    screenshot,
                    name="错误页面截图",
                    attachment_type=allure.attachment_type.PNG
                )
        
        # 验证错误信息
        assert error_msg is not None, "应该返回错误信息但没有返回"
        assert case['expected'] in error_msg

    @allure.feature("注册功能")
    @allure.story("成功场景测试")
    @pytest.mark.smoke
    @pytest.mark.parametrize("case_name", [
        pytest.param("注册成功", id="register_success"),
    ])
    def test_register_success(self, case_name):
        """测试注册成功（冒烟测试）"""
        logger.info("开始执行测试：注册成功")
        case = self._get_case_data(case_name, key="test_register_success")
        
        # Allure 动态标题和描述
        allure.dynamic.title(f"注册测试 - {case_name}")
        allure.dynamic.description(
            f"测试场景：{case_name}\n"
            f"注册方式：{case['register_way']}\n"
            f"用户名：{case['username']}"
        )
        allure.dynamic.severity(allure.severity_level.BLOCKER)
        
        # 添加测试步骤
        with allure.step(f"注册方式：{case['register_way']}"):
            pass
        with allure.step(f"用户名：{case['username']}"):
            pass
        with allure.step(f"密码：{'*' * len(case['password'])}"):
            pass
        with allure.step(f"确认密码：{'*' * len(case['confirm_pwd'])}"):
            pass
        with allure.step(f"验证码：{case['verify_code']}"):
            pass
        with allure.step(f"勾选服务协议：{case.get('check_protocol', True)}"):
            pass
        
        # 执行注册
        with allure.step("执行注册操作"):
            self.page_register.page_register(
                register_way=case['register_way'],
                username=case['username'],
                pwd=case['password'],
                confirm_pwd=case['confirm_pwd'],
                code=case['verify_code'],
                check_protocol=case.get('check_protocol', True)
            )
        
        # 验证注册成功：检查跳转到主页
        with allure.step("验证注册结果"):
            # 等待页面跳转完成（页面加载需要时间）
            import time
            time.sleep(8)  # 等待7 秒确保页面完全加载和跳转
            
            current_url = self.driver.current_url
            print(f"当前 URL: {current_url}")
            print(f"期望 URL: {self.page_register.home_url}")
            
            assert current_url == self.page_register.home_url
            
            # 截图保存
            screenshot = self.page_register.page_get_screenshot()
            if screenshot:
                allure.attach(
                    screenshot,
                    name="注册成功页面截图",
                    attachment_type=allure.attachment_type.PNG
                )
        
        # 注册成功后退出登录，返回首页，为登录测试做准备
        with allure.step("退出登录并返回首页"):
            self.page_register.page_logout()
            time.sleep(2)  # 等待退出完成
            
            # 确保返回首页（登录测试需要从首页开始）
            self.driver.get(config['url'])
            time.sleep(1)


    # 测试用户名已存在
    def test_register_username_exist(self):
        """测试用户名已存在的情况"""
        logger.info("开始执行测试：用户名已存在")
        case = self._get_case_data("用户名已存在")
        error_msg = self._execute_register(case)
        assert error_msg is not None, "应该返回错误信息但没有返回"
        assert case['expected'] in error_msg
        self.page_register.page_get_screenshot()


