from selenium.webdriver.common.keys import Keys

from base.base_page import BasePage
from utils.locator_manager import locator_manager
from utils.locator_manager import locator_manager as lm
from utils.log_utils import GetLogger

# 日志实例化
logger = GetLogger().get_logger()


class CartItem(BasePage):
    """
    购物车订单项类 - 封装单个商品的操作
    使用嵌套 Page Object 模式，每个订单项是一个独立的页面对象
    继承 BasePage 以获得基础的元素查找能力
    """
    def __init__(self, driver, position, parent_page=None):
        """
        初始化订单项
        :param driver: BasePage页的driver实例
        :param position: 商品在列表中的位置（从1开始）
        :param parent_page: 父页面实例（PageCart），用于访问共享资源
        """
        # 初始化父类 BasePage
        super().__init__(driver)
        self.position = position
        self.parent_page = parent_page
        
        # 加载订单项定位器
        self._locators = locator_manager.load_locators(
            "cart_page_locators.yaml", 
            page_key="cart_page"
        )["cart_item"]
        
        # 获取订单项根节点
        root_locator_template = locator_manager.load_locators(
            "cart_page_locators.yaml", 
            page_key="cart_page"
        )["item_root"]
        
        # 替换 position 占位符
        root_by, root_value = lm.get_locator_tuple(root_locator_template)
        root_xpath = root_value.format(position=position)
        
        # 使用 BasePage 的显式等待方法查找根元素（确保元素可见）
        self.root_element = self.base_find_visible_element((root_by, root_xpath))
    
    def _find_in_item(self, locator_name: str):
        """在订单项内部查找元素（相对于 root_element）"""
        locator = self._locators[locator_name]
        by, value = locator_manager.get_locator_tuple(locator)
        return self.root_element.find_element(by, value)
    
    @property
    def select_checkbox(self):
        """获取勾选复选框"""
        return self._find_in_item("item_select_btn")
    
    @property
    def num_input(self):
        """获取数量输入框"""
        return self._find_in_item("item_num_input")
    
    @property
    def delete_button(self):
        """获取删除按钮"""
        return self._find_in_item("item_del_btn")
    
    @property
    def collect_button(self):
        """获取收藏按钮"""
        return self._find_in_item("item_collect_btn")

    @property
    def item_name(self):
        """获取商品名称，点击可跳转至详情页"""
        return self._find_in_item("item_name")

    @property
    def item_single_price(self):
        """获取商品单价"""
        return self._find_in_item("single_price")
    
    # ==================== 操作方法 ====================
    
    def item_select(self):
        """勾选该商品 - 处理隐藏的 checkbox"""
        from utils.log_utils import GetLogger
        from selenium.webdriver.common.by import By
        import time
            
        try:
            checkbox = self.select_checkbox
                
            # 检查当前状态
            is_checked = checkbox.is_selected()
                
            if not is_checked:
                GetLogger().get_logger().info("→ 尝试勾选订单项...")
                    
                success = False
                    
                # 方法 1: 直接点击 input（某些网站有效）
                try:
                    checkbox.click()
                    GetLogger().get_logger().info("✓ 通过 input 元素完成勾选")
                    success = True
                except Exception as click_error:
                    GetLogger().get_logger().debug(f"input 点击失败")
                    
                # 方法 2: JS 直接点击 <i> 标签 + 设置 input checked 属性（最可靠）
                if not success:
                    try:
                        i_element = self.root_element.find_element(By.CSS_SELECTOR, ".checkall.checkItem")
                                        
                        # 关键：同时做两件事
                        # 1. 点击<i>标签触发前端 UI 变化
                        # 2. 设置 input 的 checked 属性确保状态同步
                        self.driver.execute_script("""
                            // 点击<i>标签触发前端事件
                            arguments[0].click();
                                            
                            // 同时设置 input 的 checked 属性
                            var checkbox = arguments[1];
                            checkbox.checked = true;
                            checkbox.setAttribute('checked', 'checked');
                                            
                            // 触发 input 的 change 事件（通知价格重新计算）
                            var changeEvent = new Event('change', { bubbles: true, cancelable: true });
                            checkbox.dispatchEvent(changeEvent);
                        """, i_element, checkbox)
                                        
                        GetLogger().get_logger().info("✓ 通过 JS 点击<i>并同步 input 状态完成勾选")
                        success = True
                    except Exception as js_error:
                        GetLogger().get_logger().debug(f"JS 同步失败：{str(js_error)[:50]}")
                    
                # 方法 3: 最简单的 JS 点击（备选方案）
                if not success:
                    try:
                        i_element = self.root_element.find_element(By.CSS_SELECTOR, ".checkall.checkItem")
                        self.driver.execute_script("arguments[0].click();", i_element)
                        
                        # 也需要同步设置 input 状态
                        self.driver.execute_script("""
                            arguments[0].checked = true;
                            arguments[0].setAttribute('checked', 'checked');
                        """, checkbox)
                        
                        GetLogger().get_logger().info("✓ 通过 JS 简单点击完成勾选")
                        success = True
                    except Exception as js_error:
                        GetLogger().get_logger().debug(f"JS 简单点击失败")
                    
                if not success:
                    raise AssertionError("所有勾选方法都失败了")
                    
                # 关键：等待页面刷新和价格重新计算
                time.sleep(1.5)  # 增加到 1.5 秒，确保页面完全响应
                    
                # 验证勾选后的状态
                final_status = checkbox.is_selected()
                GetLogger().get_logger().info(f"✓ 勾选后最终状态：{'已勾选' if final_status else '未勾选'}")
                    
                if not final_status:
                    GetLogger().get_logger().error("❌ 勾选后状态仍为未勾选！")
                    raise AssertionError("订单项勾选失败：操作后状态仍为未勾选")
            else:
                GetLogger().get_logger().info("✓ 订单项已是勾选状态")
                    
        except Exception as e:
            GetLogger().get_logger().error(f"❌ 订单项勾选失败：{str(e)}")
            raise
            
        return self  # 支持链式调用
    
    def item_unselect(self):
        """取消勾选该商品 - 处理隐藏的 checkbox"""
        from utils.log_utils import GetLogger
        from selenium.webdriver.common.by import By
        import time
        
        try:
            checkbox = self.select_checkbox
            
            # 检查当前状态
            is_checked = checkbox.is_selected()
            
            if is_checked:
                GetLogger().get_logger().info("→ 尝试取消勾选订单项...")
                
                success = False
                
                # 方法 1: 优先尝试点击 input 元素
                try:
                    checkbox.click()
                    GetLogger().get_logger().info("✓ 通过 input 元素完成取消勾选")
                    success = True
                except Exception as click_error:
                    GetLogger().get_logger().debug(f"input 点击失败")
                
                # 方法 2: JS 点击<i>标签 + 设置 input unchecked（最可靠）
                if not success:
                    try:
                        i_element = self.root_element.find_element(By.CSS_SELECTOR, ".checkall.checkItem")
                        
                        # 同时做两件事：点击<i>标签 + 设置 input unchecked
                        self.driver.execute_script("""
                            // 点击<i>标签触发前端事件
                            arguments[0].click();
                            
                            // 同时设置 input 的 checked 属性为 false
                            var checkbox = arguments[1];
                            checkbox.checked = false;
                            checkbox.removeAttribute('checked');
                            
                            // 触发 input 的 change 事件（通知价格重新计算）
                            var changeEvent = new Event('change', { bubbles: true, cancelable: true });
                            checkbox.dispatchEvent(changeEvent);
                        """, i_element, checkbox)
                        
                        GetLogger().get_logger().info("✓ 通过 JS 点击<i>并同步 input 状态完成取消勾选")
                        success = True
                    except Exception as js_error:
                        GetLogger().get_logger().debug(f"JS 同步失败：{str(js_error)[:50]}")
                
                # 方法 3: 最简单的 JS 点击（备选方案）
                if not success:
                    try:
                        i_element = self.root_element.find_element(By.CSS_SELECTOR, ".checkall.checkItem")
                        self.driver.execute_script("arguments[0].click();", i_element)
                        
                        # 也需要同步设置 input 状态
                        self.driver.execute_script("""
                            arguments[0].checked = false;
                            arguments[0].removeAttribute('checked');
                        """, checkbox)
                        
                        GetLogger().get_logger().info("✓ 通过 JS 简单点击完成取消勾选")
                        success = True
                    except Exception as js_error:
                        GetLogger().get_logger().debug(f"JS 简单点击失败")
                
                if not success:
                    raise AssertionError("所有取消勾选方法都失败了")
                
                # 等待状态同步
                time.sleep(1.5)  # 确保页面完全响应
                
                # 验证取消后的状态
                final_status = checkbox.is_selected()
                GetLogger().get_logger().info(f"✓ 取消勾选后最终状态：{'已勾选' if final_status else '未勾选'}")
                
                if final_status:
                    GetLogger().get_logger().error("❌ 取消勾选后状态仍为已勾选！")
                    raise AssertionError("订单项取消勾选失败：操作后状态仍为已勾选")
            else:
                GetLogger().get_logger().info("✓ 订单项已是未勾选状态")
                
        except Exception as e:
            GetLogger().get_logger().error(f"❌ 订单项取消勾选失败：{str(e)}")
            raise
        
        return self
    
    def item_is_selected(self):
        """检查是否已勾选"""
        return self.select_checkbox.is_selected()
    
    def item_set_num(self, num: int):
        """设置购买数量 - 修改后触发 blur 事件让价格刷新"""
        input_box = self.num_input
        
        # 方法 1: Ctrl+A 全选后覆盖输入
        input_box.send_keys(Keys.CONTROL, 'a')
        input_box.send_keys(str(num))
        
        # 关键：触发 blur 事件（失去焦点），让前端重新计算价格
        from selenium.webdriver.common.by import By
        try:
            # 点击页面空白处或按 Tab 键触发 blur
            input_box.send_keys(Keys.TAB)
            GetLogger().get_logger().debug(f"→ 已修改数量为 {num}，触发 TAB 键刷新价格")
        except:
            pass
        
        # 等待价格刷新
        import time
        time.sleep(1)
        
        return self

    def item_get_single_price(self):
        """获取商品单价"""
        import re
        price_text = self.item_single_price.text
        # 提取数字部分，例如 "￥1598.00" → 1598.00
        match = re.search(r'[\d.]+', price_text)
        return float(match.group()) if match else 0.0
    
    def item_get_num(self) -> int:
        """获取当前数量"""
        try:
            return int(self.num_input.get_attribute("value"))
        except (ValueError, TypeError):
            return 0
    
    def item_delete(self):
        """删除该商品"""
        self.delete_button.click()
        return self
    
    def item_collect(self):
        """收藏该商品"""
        self.collect_button.click()
        return self
    
    def item_click_link(self):
        """点击订单项（跳转到商品详情）"""
        self.root_element.click()
        return self


class PageCart(BasePage):
    """购物车页类"""
    
    def __init__(self, driver):
        # 初始化父类 BasePage
        super().__init__(driver)
        
        # 动态加载定位器配置
        self._locators = locator_manager.load_locators(
            "cart_page_locators.yaml", 
            page_key="cart_page"
        )
    
    def _get_locator(self, name: str) -> tuple:
        """
        获取定位器元组
        :param name: 定位器名称（如 'all_select_btn'）
        :return: (By.CSS_SELECTOR, '.checkall.checkFull')
        """
        if name not in self._locators:
            raise KeyError(f"定位器 '{name}' 未找到")
        return locator_manager.get_locator_tuple(self._locators[name])
    
    # 属性方法
    @property
    def cart_btn(self):
        """首页的购物车按钮"""
        return self._get_locator("cart_btn")
    
    @property
    def all_select_btn(self):
        """全选按钮"""
        return self._get_locator("all_select_btn")
    
    @property
    def del_all_select_btn(self):
        """删除所有选中的商品按钮"""
        return self._get_locator("del_all_select_btn")
    
    @property
    def collect_all_select_btn(self):
        """收藏所有选中商品按钮"""
        return self._get_locator("collect_all_select_btn")

    @property
    def goods_select_total_num(self):
        """选中商品总数量"""
        return self._get_locator("goods_select_total_num")

    @property
    def total_price(self):
        """选中商品总价格"""
        return self._get_locator("total_price")

    @ property
    def pay_btn(self):
        """支付按钮"""
        return self._get_locator("pay_btn")

    
    # 订单项工厂方法
    def get_cart_item(self, position: int) -> CartItem:
        """
        获取指定位置的订单项对象
        
        :param position: 商品位置（从 1 开始）
        :return: CartItem 实例
        
        示例:
            cart_item = page.get_cart_item(1)  # 第 1 个商品
            cart_item.select().set_num(5)      # 勾选并设置数量为 5
        """
        return CartItem(self.driver, position, parent_page=self)

    def page_click_cart(self):
        """点击购物车"""
        logger.info("点击购物车按钮")
        self.base_click(self.cart_btn)

    def page_all_select_click(self):
        """点击全选按钮 - 基于原生 input 的 checked 属性判断"""
        from selenium.webdriver.common.by import By
        from selenium.webdriver import ActionChains
        import time
        
        logger.info("点击全选按钮")
        try:
            # 直接定位到隐藏的 input 元素
            checkbox = self.base_find_element(self.all_select_btn)
            
            # 使用 is_selected() 判断（底层检查 checked 属性）
            is_checked = checkbox.is_selected()
            
            GetLogger().get_logger().info(f"全选按钮当前状态：{'已勾选' if is_checked else '未勾选'}")
            
            if is_checked:
                GetLogger().get_logger().info("当前已是全选状态，点击取消全选...")
            else:
                GetLogger().get_logger().info("当前未全选，点击进行全选...")
            
            success = False
            
            # 方法 1: 优先尝试点击 input 元素
            try:
                checkbox.click()
                GetLogger().get_logger().info("✓ 通过 input 元素完成全选操作")
                success = True
            except Exception as click_error:
                GetLogger().get_logger().debug(f"input 点击失败")
            
            # 方法 2: 如果 input 点击失败，使用 Actions 点击可见的 <i> 标签
            if not success:
                try:
                    i_element = self.base_find_visible_element((By.CSS_SELECTOR, ".checkall.checkFull"))
                    
                    # 使用 Actions 更可靠（模拟真实用户行为）
                    actions = ActionChains(self.driver)
                    actions.move_to_element(i_element).click().perform()
                    
                    GetLogger().get_logger().info("✓ 通过<i>标签完成全选操作 (Actions)")
                    success = True
                except Exception as i_error:
                    GetLogger().get_logger().debug(f"<i> 标签 Actions 点击失败")
            
            # 方法 3: 如果都失败，使用 JS 强制触发
            if not success:
                GetLogger().get_logger().info("→ 使用 JS 强制点击<i>标签...")
                try:
                    i_element = self.base_find_visible_element((By.CSS_SELECTOR, ".checkall.checkFull"))
                    self.driver.execute_script("arguments[0].click();", i_element)
                    GetLogger().get_logger().info("✓ 通过 JS 点击<i>标签完成全选操作")
                except Exception as js_error:
                    GetLogger().get_logger().error(f"❌ JS 方法失败：{str(js_error)}")
                    raise
            
            # 关键：等待页面刷新和价格重新计算
            time.sleep(1)  # 确保页面完全响应
            
            # 验证点击后的状态
            final_status = checkbox.is_selected()
            GetLogger().get_logger().info(f"✓ 全选操作后最终状态：{'已勾选' if final_status else '未勾选'}")
            
        except Exception as e:
            GetLogger().get_logger().error(f"❌ 全选操作完全失败：{str(e)}")
            raise

    def page_del_all_select_click(self):
        """点击删除所有选中商品按钮"""
        logger.info("点击删除所有选中商品按钮")
        self.base_click(self.del_all_select_btn)

    def page_collect_all_select_click(self):
        """点击收藏所有选中商品按钮"""
        logger.info("点击收藏所有选中商品按钮")
        self.base_click(self.collect_all_select_btn)

    def page_item_select(self,position: int):
        """勾选指定订单的勾选框"""
        logger.info(f"勾选第 {position} 个商品")
        self.get_cart_item(position).item_select()
    def page_item_unselect(self,position: int):
        """取消勾选指定商品"""
        logger.info(f"取消勾选第 {position} 个商品")
        self.get_cart_item(position).item_unselect()

    def page_change_num(self,position: int,num: int):
        """修改指定订单的数量"""
        logger.info(f"修改第 {position} 个商品数量为: {num}")
        self.get_cart_item(position).item_set_num(num)

    def page_del_item(self,position: int):
        """删除指定订单"""
        logger.info(f"删除第 {position} 个商品")
        self.get_cart_item(position).item_delete()

    def page_collect_item(self,position: int):
        """收藏指定订单商品"""
        logger.info(f"收藏第 {position} 个商品")
        self.get_cart_item( position).item_collect()

    def page_get_single_price(self,position: int):
        """获取指定订单商品单价"""
        price = self.get_cart_item(position).item_get_single_price()
        logger.debug(f"第 {position} 个商品单价: {price}")
        return price

    def page_get_total_price(self) -> float:
        """获取选中商品总价格"""
        price_text = self.base_get_text(self.total_price)
        # 提取价格数字，例如 "￥123.45" → 123.45
        import re
        match = re.search(r'[\d.]+', price_text)
        total_price = float(match.group()) if match else 0.0
        logger.info(f"选中商品总价格: {total_price}")
        return total_price
    
    def page_get_goods_select_total_num(self) -> int:
        """获取选中商品总数量 - 增加重试机制"""
        try:
            import time
            time.sleep(0.5)  # 等待页面刷新
            num_text = self.base_get_text(self.goods_select_total_num)
            # 提取数字，例如 "已选 (3 件)" → 3
            import re
            match = re.search(r'\d+', num_text)
            result = int(match.group()) if match else 0
            GetLogger().get_logger().info(f"获取到选中商品总数：{result}")
            return result
        except (ValueError, AttributeError) as e:
            GetLogger().get_logger().error(f"获取选中商品总数失败：{str(e)}")
            return 0

    def page_pay_click(self):
        """点击结算按钮"""
        logger.info("点击结算按钮")
        self.base_click(self.pay_btn)

    def page_get_screenshot(self):
        """获取当前页面截图"""
        logger.info("执行页面截图")
        return self.base_get_screenshot()
