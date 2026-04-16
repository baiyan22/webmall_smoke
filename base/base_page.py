import time
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.log_utils import GetLogger

logger = GetLogger().get_logger()


class BasePage:
    def __init__(self, driver: WebDriver):
        """
        初始化 BasePage
        rgs: driver: WebDriver 对象（由 pytest fixture 或 DriverManager 提供）
        """
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        logger.debug("BasePage 初始化完成")

    #打开目标url
    def open_url(self,url):
        logger.debug(f"打开 URL: {url}")
        self.driver.get(url)
        logger.debug(f"URL 加载完成: {self.driver.current_url}")

    #显式等待
    def wait_element(self,loc,timeout=10,poll_frequency=0.5):
        """
        :param loc:元素配置信息，元组格式，，eg：loc=By.ID，'#username' ,元组可以不带外面的小括号，传入时用*解包即可
        :param timeout:默认超时时间 10s
        :param poll_frequency:默认访问频率 0.5s
        :return: 查找的元素
        """
        logger.debug(f"等待元素: {loc}, 超时时间: {timeout}s")
        try:
            element = WebDriverWait(self.driver, timeout, poll_frequency).until(lambda x: x.find_element(*loc))
            logger.debug(f"元素找到: {loc}")
            return element
        except Exception as e:
            logger.error(f"元素未找到: {loc}, 错误: {str(e)}")
            raise

    # 定位元素
    def base_find_element(self, loc):
        logger.debug(f"定位元素: {loc}")
        return self.wait_element(loc)

    # 定位可见元素（等待元素可见后再返回）
    def base_find_visible_element(self, loc, timeout=10):
        """
        等待元素可见后再返回，适用于需要交互的元素
        :param loc: 元素配置信息
        :param timeout: 超时时间
        :return: 可见的元素
        """
        logger.debug(f"等待元素可见: {loc}, 超时: {timeout}s")
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(loc)
            )
            logger.debug(f"元素可见: {loc}")
            return element
        except Exception as e:
            logger.error(f"元素不可见: {loc}, 错误: {str(e)}")
            raise

    # 定位可点击元素（等待元素可点击后再返回）
    def base_find_clickable_element(self, loc, timeout=10):
        """
        等待元素可点击后再返回，比 visible 更严格
        :param loc: 元素配置信息
        :param timeout: 超时时间
        :return: 可点击的元素
        """
        logger.debug(f"等待元素可点击: {loc}, 超时: {timeout}s")
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(loc)
            )
            logger.debug(f"元素可点击: {loc}")
            return element
        except Exception as e:
            logger.error(f"元素不可点击: {loc}, 错误: {str(e)}")
            raise

    # 点击元素
    def base_click(self, loc):
        """
        点击元素（智能处理可能被遮挡的情况）
        策略：先尝试普通点击 → 失败则移除遮罩层 → 再失败则使用 JS 点击
        :param loc: 元素定位信息
        """
        logger.debug(f"点击元素: {loc}")
        element = self.base_find_element(loc)
        
        try:
            # 第一层：尝试正常点击
            element.click()
            logger.debug("普通点击成功")
        except Exception as e:
            logger.warning(f"普通点击失败，尝试移除遮罩层: {str(e)}")
            
            try:
                # 第二层：尝试移除遮罩层后再次点击
                self.base_js_remove_overlay('.layui-layer-shade')
                element.click()
                logger.debug("✓ 移除遮罩层后点击成功")
            except Exception as e2:
                logger.warning(f"移除遮罩层后仍失败，使用 JS 强制点击: {str(e2)}")
                
                try:
                    # 第三层：使用 JS 强制点击
                    self.base_js_click(loc)
                    logger.debug("JS 强制点击成功")
                except Exception as e3:
                    logger.error(f"所有点击方式均失败: {str(e3)}")
                    raise

    # 输入元素
    def base_input(self, loc, keys):
        logger.debug(f"输入内容到元素 {loc}: {'*' * len(str(keys)) if 'pwd' in str(loc).lower() or 'password' in str(loc).lower() else keys}")
        el = self.base_find_element(loc)
        # 清空输入框
        el.clear()
        # 输入
        el.send_keys(keys)
        logger.debug("输入完成")

    #获取文本方法
    def base_get_text(self,loc):
        logger.debug(f"获取元素文本: {loc}")
        text = self.base_find_element(loc).text
        logger.debug(f"获取到的文本: {text[:50] if len(text) > 50 else text}")
        return text

    #截图方法
    def base_get_screenshot(self):
        """截取当前页面并保存到 image 目录，同时返回 PNG 数据"""
        import os
        logger.debug("执行页面截图")
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
        logger.debug(f"截图已保存：{filepath}")
        # 返回 PNG 格式的二进制数据（用于 Allure 附件）
        return self.driver.get_screenshot_as_png()

    # ==================== 窗口与框架处理方法 ====================
    
    def base_switch_to_window(self, window_index=-1):
        """
        切换到指定窗口
        :param window_index: 窗口索引，默认为 -1（最新打开的窗口），0 为主窗口
        :return: 切换后的窗口句柄
        """
        logger.debug(f"切换到窗口，索引: {window_index}")
        try:
            all_windows = self.driver.window_handles
            if len(all_windows) == 0:
                raise Exception("没有可用的窗口")
            if abs(window_index) > len(all_windows):
                raise Exception(f"窗口索引 {window_index} 超出范围，当前窗口数: {len(all_windows)}")
            
            target_window = all_windows[window_index]
            self.driver.switch_to.window(target_window)
            logger.debug(f"✓ 成功切换到窗口: {target_window}, 当前 URL: {self.driver.current_url}")
            return target_window
        except Exception as e:
            logger.error(f"✗ 切换窗口失败: {str(e)}")
            raise

    def switch_to_window_by_title(self, title_keyword):
        """
        根据标题关键字切换到指定窗口
        :param title_keyword: 窗口标题包含的关键字
        :return: 切换后的窗口句柄
        """
        logger.debug(f"根据标题关键字切换窗口: {title_keyword}")
        try:
            current_handle = self.driver.current_window_handle
            all_windows = self.driver.window_handles
            
            for handle in all_windows:
                if handle != current_handle:
                    self.driver.switch_to.window(handle)
                    if title_keyword in self.driver.title:
                        logger.debug(f"✓ 找到匹配窗口: {self.driver.title}, 句柄: {handle}")
                        return handle
            
            # 如果没有找到，切回原窗口
            self.driver.switch_to.window(current_handle)
            raise Exception(f"未找到标题包含 '{title_keyword}' 的窗口")
        except Exception as e:
            logger.error(f"✗ 根据标题切换窗口失败: {str(e)}")
            raise

    def base_switch_to_window_by_url(self, url_keyword):
        """
        根据 URL 关键字切换到指定窗口
        :param url_keyword: URL 包含的关键字
        :return: 切换后的窗口句柄
        """
        logger.debug(f"根据 URL 关键字切换窗口: {url_keyword}")
        try:
            current_handle = self.driver.current_window_handle
            all_windows = self.driver.window_handles
            
            for handle in all_windows:
                if handle != current_handle:
                    self.driver.switch_to.window(handle)
                    if url_keyword in self.driver.current_url:
                        logger.debug(f"✓ 找到匹配窗口: {self.driver.current_url}, 句柄: {handle}")
                        return handle
            
            # 如果没有找到，切回原窗口
            self.driver.switch_to.window(current_handle)
            raise Exception(f"未找到 URL 包含 '{url_keyword}' 的窗口")
        except Exception as e:
            logger.error(f"✗ 根据 URL 切换窗口失败: {str(e)}")
            raise

    def base_close_current_window(self):
        """
        关闭当前窗口，并自动切换回主窗口
        :return: 切换后的窗口句柄
        """
        logger.debug("关闭当前窗口")
        try:
            current_handle = self.driver.current_window_handle
            self.driver.close()
            logger.debug(f"已关闭窗口: {current_handle}")
            
            # 切换到剩余的第一个窗口
            remaining_windows = self.driver.window_handles
            if remaining_windows:
                self.driver.switch_to.window(remaining_windows[0])
                logger.debug(f"已切换到窗口: {remaining_windows[0]}")
                return remaining_windows[0]
            else:
                logger.warning("所有窗口已关闭")
                return None
        except Exception as e:
            logger.error(f"关闭窗口失败: {str(e)}")
            raise

    def base_get_all_windows(self):
        """
        获取所有窗口句柄
        :return: 窗口句柄列表
        """
        logger.debug("获取所有窗口句柄")
        windows = self.driver.window_handles
        logger.debug(f"当前窗口数量: {len(windows)}")
        for i, win in enumerate(windows):
            logger.debug(f"  窗口 {i}: {win}")
        return windows

    def base_switch_to_iframe(self, iframe_locator):
        """
        切换到 iframe
        :param iframe_locator: iframe 元素定位信息
        :return: iframe 元素
        """
        logger.debug(f"切换到 iframe: {iframe_locator}")
        try:
            iframe_element = self.base_find_element(iframe_locator)
            self.driver.switch_to.frame(iframe_element)
            logger.debug(f"成功切换到 iframe")
            return iframe_element
        except Exception as e:
            logger.error(f"切换到 iframe 失败: {str(e)}")
            raise

    def base_switch_to_iframe_by_index(self, index):
        """
        根据索引切换到 iframe
        :param index: iframe 索引（从 0 开始）
        """
        logger.debug(f"根据索引切换到 iframe: {index}")
        try:
            self.driver.switch_to.frame(index)
            logger.debug(f"成功切换到第 {index} 个 iframe")
        except Exception as e:
            logger.error(f"切换到 iframe 失败: {str(e)}")
            raise

    def base_switch_to_iframe_by_name(self, name):
        """
        根据 name 或 id 切换到 iframe
        :param name: iframe 的 name 或 id 属性值
        """
        logger.debug(f"根据 name/id 切换到 iframe: {name}")
        try:
            self.driver.switch_to.frame(name)
            logger.debug(f"成功切换到 iframe: {name}")
        except Exception as e:
            logger.error(f"切换到 iframe 失败: {str(e)}")
            raise

    def base_switch_to_default_content(self):
        """
        从 iframe 切换回主文档
        """
        logger.debug("从 iframe 切换回主文档")
        try:
            self.driver.switch_to.default_content()
            logger.debug("已成功切换回主文档")
        except Exception as e:
            logger.error(f"切换回主文档失败: {str(e)}")
            raise

    def base_switch_to_parent_frame(self):
        """
        从子 iframe 切换到父 iframe
        """
        logger.debug("从子 iframe 切换到父 iframe")
        try:
            self.driver.switch_to.parent_frame()
            logger.debug("已成功切换到父 iframe")
        except Exception as e:
            logger.error(f"切换到父 iframe 失败: {str(e)}")
            raise

    # ==================== JS 执行方法 ====================

    def base_js_click(self, loc):
        """
        使用 JavaScript 点击元素（适用于被遮挡或普通点击无效的情况）
        :param loc: 元素定位信息
        """
        logger.debug(f"使用 JS 点击元素: {loc}")
        try:
            element = self.base_find_element(loc)
            self.driver.execute_script("arguments[0].click();", element)
            logger.debug("JS 点击成功")
        except Exception as e:
            logger.error(f"JS 点击失败: {str(e)}")
            raise

    def base_js_scroll_to_element(self, loc):
        """
        滚动页面到指定元素位置
        :param loc: 元素定位信息
        """
        logger.debug(f"滚动到元素: {loc}")
        try:
            element = self.base_find_element(loc)
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            logger.debug("已滚动到元素位置")
        except Exception as e:
            logger.error(f"滚动到元素失败: {str(e)}")
            raise

    def base_js_scroll_to_bottom(self):
        """
        滚动到页面底部
        """
        logger.debug("滚动到页面底部")
        try:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            logger.debug("已滚动到页面底部")
        except Exception as e:
            logger.error(f"滚动到底部失败: {str(e)}")
            raise

    def base_js_scroll_to_top(self):
        """
        滚动到页面顶部
        """
        logger.debug("滚动到页面顶部")
        try:
            self.driver.execute_script("window.scrollTo(0, 0);")
            logger.debug("已滚动到页面顶部")
        except Exception as e:
            logger.error(f"滚动到顶部失败: {str(e)}")
            raise

    def base_js_remove_overlay(self, selector='.layui-layer-shade'):
        """
        移除遮罩层（默认移除 layui 遮罩层）
        :param selector: 遮罩层的 CSS 选择器，默认为 '.layui-layer-shade'
        """
        logger.debug(f"移除遮罩层: {selector}")
        try:
            # 尝试查找并移除遮罩层
            result = self.driver.execute_script(
                f"""
                var overlays = document.querySelectorAll('{selector}');
                var count = overlays.length;
                for(var i = 0; i < overlays.length; i++) {{
                    overlays[i].remove();
                }}
                return count;
                """
            )
            if result > 0:
                logger.debug(f"已移除 {result} 个遮罩层")
            else:
                logger.debug("未找到遮罩层")
        except Exception as e:
            logger.warning(f"移除遮罩层异常: {str(e)}")

    def base_js_set_value(self, loc, value):
        """
        使用 JavaScript 设置元素的值（适用于 input 等表单元素）
        :param loc: 元素定位信息
        :param value: 要设置的值
        """
        logger.debug(f"使用 JS 设置元素值: {loc}, 值: {'*' * len(str(value)) if 'pwd' in str(loc).lower() or 'password' in str(loc).lower() else value}")
        try:
            element = self.base_find_element(loc)
            self.driver.execute_script("arguments[0].value = arguments[1];", element, value)
            logger.debug("JS 设置值成功")
        except Exception as e:
            logger.error(f"JS 设置值失败: {str(e)}")
            raise

    def base_js_get_attribute(self, loc, attribute):
        """
        使用 JavaScript 获取元素属性
        :param loc: 元素定位信息
        :param attribute: 属性名称
        :return: 属性值
        """
        logger.debug(f"使用 JS 获取元素属性: {loc}, 属性: {attribute}")
        try:
            element = self.base_find_element(loc)
            value = self.driver.execute_script("return arguments[0].getAttribute(arguments[1]);", element, attribute)
            logger.debug(f"获取到属性值: {value}")
            return value
        except Exception as e:
            logger.error(f"JS 获取属性失败: {str(e)}")
            raise

    def base_js_execute(self, script, *args):
        """
        执行自定义 JavaScript 代码
        :param script: JavaScript 代码字符串
        :param args: 传递给 JS 的参数
        :return: JS 执行结果
        """
        logger.debug(f"执行自定义 JS: {script[:50]}...")
        try:
            result = self.driver.execute_script(script, *args)
            logger.debug("JS 执行成功")
            return result
        except Exception as e:
            logger.error(f"JS 执行失败: {str(e)}")
            raise



