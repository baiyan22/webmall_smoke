from base.base_page import BasePage
from selenium.webdriver.common.by import By
from pages.page_search import PageSearch
from utils.log_utils import GetLogger

logger = GetLogger().get_logger()

class PageGoodDetail(BasePage):
    """商品详情页类"""

    #加入购物车按钮
    add_cart_btn=By.CSS_SELECTOR,".addcar.buy_button"
    #立即购买按钮
    initial_btn=By.CSS_SELECTOR,".paybybill.buy_button"

    #配送地址 - 使用动态 XPath 拼接
    address_btn=By.CSS_SELECTOR,".goods_dispatching_name"
    #省份选择按钮
    province_btn=By.XPATH,"//*[@id='buy_goods_form']/div/div[3]/ul/li[2]/div/div/div[2]/div/div[1]/ul/li[1]"
    #省份列表容器（用于拼接动态 XPath）
    province_container = "//*[@id='buy_goods_form']/div/div[3]/ul/li[2]/div/div/div[2]/div/div[2]/ul"
    #城市选择按钮
    city_btn=By.XPATH,"//*[@id='buy_goods_form']/div/div[3]/ul/li[2]/div/div/div[2]/div/div[1]/ul/li[2]"
    #城市列表容器（用于拼接动态 XPath）
    city_container = "//*[@id='buy_goods_form']/div/div[3]/ul/li[2]/div/div/div[2]/div/div[3]/ul"
    #区县选择按钮
    area_btn=By.XPATH,"//*[@id='buy_goods_form']/div/div[3]/ul/li[2]/div/div/div[2]/div/div[1]/ul/li[3]"
    #区县列表容器（用于拼接动态 XPath）
    area_container = "//*[@id='buy_goods_form']/div/div[3]/ul/li[2]/div/div/div[2]/div/div[4]/ul"

    #商品数量，有自修正功能，非正数自动跳为1，超过库存数时跳为库存数
    good_num=By.XPATH,"//*[@id='number']"
    #商品数量减1
    reduce_num=By.XPATH,"//*[@id='buy_goods_form']/div/div[5]/ul/li[2]/div[1]/a[1]"
    #数量加1
    add_num=By.XPATH,"//*[@id='buy_goods_form']/div/div[5]/ul/li[2]/div[1]/a[2]"

    # 购物车内商品数量 (角标)
    cart_nums = By.CSS_SELECTOR, ".shop-nums"
    # 加入成功提示框关闭按钮
    close_add_success = By.CSS_SELECTOR, "#layui-layer1 > span > a"

    #收藏商品按钮
    collect_goods=By.CSS_SELECTOR,".collect-text"

    def page_get_url(self):
        """获取当前页面 URL"""
        url = self.driver.current_url
        logger.debug(f"当前页面 URL: {url}")
        return url


    def page_search_and_click_item(self,key,good_position):
        """搜索并点击商品"""
        logger.info(f"搜索并点击商品 - 关键词: {key}, 位置: {good_position}")
        PageSearch(self.driver).page_search_and_click_item(key,good_position)




    def page_input_and_get_address(self, position1, position2, position3):
        """选择配送地址 - 使用字符串拼接动态 XPath"""
        logger.info("="*30 + " 开始选择配送地址 " + "="*30)
        # 等待商品详情页完全加载（检查页面特征元素）
        try:
            # 等待加入购物车按钮可见，确认页面已加载
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(self.add_cart_btn)
            )
            logger.info("✓ 商品详情页加载完成")
        except Exception as e:
            logger.error(f"⚠ 等待商品详情页超时：{str(e)}")
            # 截图查看当前页面状态
            screenshot = self.driver.get_screenshot_as_png()
            with open("debug_page_not_loaded.png", "wb") as f:
                f.write(screenshot)
            logger.error("→ 已保存调试截图：debug_page_not_loaded.png")
            raise

        #点击配送地址按钮开始设置
        logger.info("点击配送地址按钮")
        self.base_click(self.address_btn)
        
        # 直接拼接完整 XPath
        province_xpath = f"{self.province_container}/li[{position1}]/a"
        city_xpath = f"{self.city_container}/li[{position2}]/a"
        area_xpath = f"{self.area_container}/li[{position3}]/a"

        p_address = By.XPATH, province_xpath
        c_address = By.XPATH, city_xpath
        a_address = By.XPATH, area_xpath

        # 依次点击省市区
        logger.info("→ 开始选择省份...")
        self.base_click(self.province_btn)
        p_text = self.base_get_text(p_address)
        self.base_click(p_address)
        logger.info(f"✓ 已选择省份：{p_text}")
        
        logger.info("→ 开始选择城市...")
        self.base_click(self.city_btn)
        c_text = self.base_get_text(c_address)
        self.base_click(c_address)
        logger.info(f"✓ 已选择城市：{c_text}")

        logger.info("→ 开始选择区县...")
        self.base_click(self.area_btn)
        a_text = self.base_get_text(a_address)
        self.base_click(a_address)
        logger.info(f"✓ 已选择区县：{a_text}")

        logger.info("="*30 + " 配送地址选择完成 " + "="*30)
        return p_text, c_text, a_text


    def page_input_num(self, num):
        """输入购买商品数 - 使用全选后覆盖的方式更可靠"""
        from selenium.webdriver.common.keys import Keys
        
        logger.info(f"设置商品数量为: {num}")
        # 方法 1：使用 Ctrl+A 全选后直接输入新值（最可靠）
        element = self.base_find_element(self.good_num)
        element.click()  # 先聚焦
        element.send_keys(Keys.CONTROL, 'a')  # 全选
        element.send_keys(str(num))  # 直接覆盖输入
        logger.debug("数量设置完成")
        
        # 方法 2（备选）：如果 Ctrl+A 无效，使用 base_input 的 clear+send_keys
        # self.base_input(self.good_num, str(num))

    def page_add_num(self):
        """点击数量加1按钮"""
        logger.info("点击数量加1按钮")
        self.base_click(self.add_num)

    def page_reduce_num(self):
        """点击数量减1按钮"""
        logger.info("点击数量减1按钮")
        self.base_click(self.reduce_num)

    def page_add_cart(self):
        """点击加入购物车按钮 ---buy_type=cart时使用"""
        logger.info("点击加入购物车按钮")
        self.base_click(self.add_cart_btn)

    def page_close_add_success(self):
        """关闭加入成功提示框"""
        logger.info("关闭加入购物车成功提示框")
        self.base_click(self.close_add_success)

    def page_buy_now(self):
        """点击立即购买按钮"""
        logger.info("点击立即购买按钮")
        self.base_click(self.initial_btn)

    def page_get_cart_num(self):
        """获取购物车角标数量"""
        cart_num = self.base_get_text(self.cart_nums)
        logger.info(f"购物车商品数量: {cart_num}")
        return cart_num

    def page_get_screenshot(self):
        """获取当前页面截图"""
        logger.info("执行页面截图")
        return self.base_get_screenshot()



