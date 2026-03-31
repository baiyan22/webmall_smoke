from selenium.webdriver.common.by import By

from base.base_page import BasePage


class PageRegister(BasePage):
    """注册页面配置"""
    #注册链接
    register_link=By.PARTIAL_LINK_TEXT,"注册"

    """手机注册"""
    #手机注册页面
    phone_register_link=By.PARTIAL_LINK_TEXT,"手机注册"
    #手机号
    phone_number=By.CSS_SELECTOR,".inp.fmobile.J_cellphone"
    #手机图像验证码
    phone_verify_code=By.CSS_SELECTOR,'[name="verify_code"]'

    """邮箱注册"""
    #邮箱注册页面
    email_register_link=By.PARTIAL_LINK_TEXT,"邮箱注册"
    #邮箱
    email=By.CSS_SELECTOR,".inp.J_cellphone"
    #邮箱图像验证码，8888
    email_verify_code=By.CSS_SELECTOR,'[name="verify_code2"]'

    # 设置密码，6-16位大小写英文字母、数字或符号的组合
    register_pwd = By.ID, 'password'
    # 确认密码
    confirm_pwd = By.ID, "password2"

    #推荐人手机号（非必填）
    invite_phone=By.CSS_SELECTOR,'[name="invite"]'

    #注册按钮
    register_btn=By.CSS_SELECTOR,'.regbtn.J_btn_agree'

    #异常文本信息
    register_err_info=By.CSS_SELECTOR,'.layui-layer-content'

    #异常提示确认
    register_err_info_btn=By.ID,'.layui-layer-btn0'
    
    # 用户协议复选框
    protocol_checkbox = By.ID, "checktxt"

    #用户中心url, /index.php/
    user_center_url = 'https://hmshop-test.itheima.net/Home/user/index.html'

    #首页url, /index.php/
    home_url = 'https://hmshop-test.itheima.net/Home/Index/index.html'

    # 退出登录
    logout_link = By.PARTIAL_LINK_TEXT, "退出"

    def __init__(self, driver):
        super().__init__(driver)  # 调用父类构造函数


    # 点击注册链接
    def page_click_register_link(self):
        self.base_click(self.register_link)

    #选择注册方式
    def page_select_register_way(self, register_way):
        if register_way == "phone":
            self.base_click(self.phone_register_link)
        elif register_way == "email":
            self.base_click(self.email_register_link)
        else:
            raise ValueError("无效的注册方式")

    # 输入用户名
    def page_input_username(self, username):
        """
        根据用户名内容选择输入到手机号或邮箱输入框
        
        Args:
            username: 用户名（手机号或邮箱）
        """
        # 简单判断：包含 @ 就认为是邮箱，否则是手机号
        # 注意：这里不做格式验证，格式验证由前端/后端负责
        if '@' in str(username):
            print(f"→ 输入邮箱：{username}")
            self.base_input(self.email, username)
        else:
            print(f"→ 输入手机号：{username}")
            self.base_input(self.phone_number, username)


    # 输入密码
    def page_input_pwd(self, pwd):
        self.base_input(self.register_pwd, pwd)

    #确认密码
    def page_confirm_pwd(self, confirm_pwd):
        self.base_input(self.confirm_pwd, confirm_pwd)

    # 输入验证码
    def page_input_code(self, code):
         self.base_input(self.phone_verify_code, code)

    # 用户协议
    def page_ensure_protocol_checked(self):
        """
        确保用户协议复选框一定被勾选
        逻辑：先判断 → 未勾选则勾选 → 触发事件 → 最终验证
            
        Returns:
            bool: 返回最终勾选状态
            
        Raises:
            AssertionError: 当复选框无法被勾选时抛出异常
        """
        try:
            # 1. 定位复选框（使用显式等待）
            checkbox = self.wait_element(self.protocol_checkbox, timeout=10)
                
            # 2. 获取当前是否勾选
            is_checked = checkbox.is_selected()
            print(f"✓ 初始勾选状态：{is_checked}")
                
            # 3. 未勾选 → 执行勾选
            if not is_checked:
                print("→ 执行勾选操作...")
                    
                # 方法 1: JS 强制勾选（推荐，避免页面 JS 干扰）
                self.driver.execute_script("arguments[0].checked = true;", checkbox)
                self.driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", checkbox)
                    
                # 可选：方法 2 - 直接点击（如果 JS 方式不起作用可切换）
                # checkbox.click()
                    
                print("✓ 勾选完成")
                
            # 4. 最终验证：确保一定是勾选状态
            final_status = checkbox.is_selected()
            print(f"✓ 最终验证状态：{final_status}")
                
            # 5. 断言验证
            assert final_status is True, "用户协议勾选失败！"
                
            return final_status
                
        except Exception as e:
            # 截图保存错误现场
            self.page_get_screenshot()
            raise AssertionError(f"处理用户协议复选框时发生错误：{str(e)}")

    def page_uncheck_protocol(self):
        """
        取消勾选用户协议 (用于测试不勾选协议的场景)
        逻辑：强制取消勾选 → 触发事件 → 验证状态
        """
        try:
            # 1. 定位复选框
            checkbox = self.wait_element(self.protocol_checkbox, timeout=10)
            
            # 2. 使用 JS 强制取消勾选
            self.driver.execute_script("arguments[0].checked = false;", checkbox)
            self.driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", checkbox)
            
            # 3. 验证确实已取消
            final_status = checkbox.is_selected()
            print(f"✗ 取消勾选后状态：{final_status}")
            
            # 4. 断言验证
            assert final_status is False, "用户协议取消勾选失败！"
            
            return final_status
            
        except Exception as e:
            self.page_get_screenshot()
            raise AssertionError(f"取消勾选用户协议时发生错误：{str(e)}")


    # 点击注册按钮
    def page_click_register_btn(self):
        self.base_click(self.register_btn)

    # 获取异常信息
    def page_get_err_info(self):
        """获取错误提示信息（带等待）"""
        import time
        time.sleep(1)  # 等待提示框出现
        try:
             return self.base_get_text(self.register_err_info)
        except:
               print("未找到错误提示元素")
               return None

    # 点击异常信息按钮
    def page_click_err_info_btn(self):
        self.base_click(self.register_err_info_btn)

    # 截图
    def page_get_screenshot(self):
        self.base_get_screenshot()

    #退出登录
    def page_logout(self):
        self.base_click(self.logout_link)


    #业务组合
    def page_register(self, register_way, username, pwd, confirm_pwd, code, check_protocol=True):
        """
        完整的注册流程
        
        Args:
            register_way: 注册方式（"phone" 或 "email"）
            username: 用户名（手机号或邮箱）
            pwd: 密码
            confirm_pwd: 确认密码
            code: 验证码
            check_protocol: 是否勾选用户协议（默认 True）
        """
        self.page_click_register_link()
        self.page_select_register_way(register_way)
        self.page_input_username(username)
        self.page_input_pwd(pwd)
        self.page_confirm_pwd(confirm_pwd)
        self.page_input_code(code)
        
        # 根据参数决定是否勾选协议
        if check_protocol:
            print("✓ 参数指示：需要勾选用户协议")
            self.page_ensure_protocol_checked()
        else:
            print("✗ 参数指示：不勾选用户协议 (测试场景)")
            # 关键：主动取消勾选，防止页面自动勾选
            self.page_uncheck_protocol()
        
        self.page_click_register_btn()

        