import time
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class BasePage():
    def __init__(self, driver: WebDriver):
        """
        初始化 BasePage
        rgs: driver: WebDriver 对象（由 pytest fixture 或 DriverManager 提供）
        """
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    #打开目标url
    def open_url(self,url):
        self.driver.get(url)

    #显式等待
    def wait_element(self,loc,timeout=10,poll_frequency=0.5):
        """
        :param loc:元素配置信息，元组格式，，eg：loc=By.ID，'#username' ,元组可以不带外面的小括号，传入时用*解包即可
        :param timeout:默认超时时间 10s
        :param poll_frequency:默认访问频率 0.5s
        :return: 查找的元素
        """
        return WebDriverWait(self.driver, timeout, poll_frequency).until(lambda x: x.find_element(*loc))

    # 定位元素
    def base_find_element(self, loc):
        return self.wait_element(loc)

    # 定位可见元素（等待元素可见后再返回）
    def base_find_visible_element(self, loc, timeout=10):
        """
        等待元素可见后再返回，适用于需要交互的元素
        :param loc: 元素配置信息
        :param timeout: 超时时间
        :return: 可见的元素
        """
        return WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(loc)
        )

    # 定位可点击元素（等待元素可点击后再返回）
    def base_find_clickable_element(self, loc, timeout=10):
        """
        等待元素可点击后再返回，比 visible 更严格
        :param loc: 元素配置信息
        :param timeout: 超时时间
        :return: 可点击的元素
        """
        return WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable(loc)
        )

    # 点击元素
    def base_click(self, loc):
        """
        点击元素（处理可能被遮挡的情况）
         Args: loc: 元素定位信息
        """
        element = self.base_find_element(loc)
        try:
            # 尝试正常点击
            element.click()
        except Exception as e:
            # 如果被遮挡，先尝试移除遮罩层
            print(f"正常点击失败，尝试移除遮罩层：{str(e)}")
            try:
                # 查找并移除 layui 遮罩层
                shade_layer = self.driver.find_element(By.CSS_SELECTOR, '.layui-layer-shade')
                if shade_layer:
                    self.driver.execute_script("arguments[0].remove();", shade_layer)
                    print("✓ 已移除 layui 遮罩层")
            except:
                print("→ 未找到遮罩层或使用 JS 强制点击")
            
            # 使用 JS 强制点击目标元素
            self.driver.execute_script("arguments[0].click();", element)

    # 输入元素
    def base_input(self, loc, keys):
        el = self.base_find_element(loc)
        # 清空输入框
        el.clear()
        # 输入
        el.send_keys(keys)

    #获取文本方法
    def base_get_text(self,loc):
        return self.base_find_element(loc).text

    #截图方法
    def base_get_screenshot(self):
        """截取当前页面并保存到 image 目录，同时返回 PNG 数据"""
        import os
        # 获取项目根目录
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # 创建 image 目录（如果不存在）
        image_dir = os.path.join(project_root, 'image')
        if not os.path.exists(image_dir):
            os.makedirs(image_dir)
        # 生成文件名
        filename = time.strftime('%Y%m%d_%H%M%S') + '.png'
        filepath = os.path.join(image_dir, filename)
        # 保存截图到文件
        self.driver.get_screenshot_as_file(filepath)
        print(f"截图已保存：{filepath}")
        # 返回 PNG 格式的二进制数据（用于 Allure 附件）
        return self.driver.get_screenshot_as_png()



