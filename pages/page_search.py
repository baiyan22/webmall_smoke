from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

from base.base_page import BasePage


class GoodsItem(BasePage):
    """商品项配置"""
    
    def __init__(self, driver, item_element):
        # 初始化父类 BasePage
        super().__init__(driver)
        # item：传入单个商品的根元素（作为查找子元素的上下文）
        self.context = item_element
        # 单个商品内私有元素定位
        #数量
        self.num_input = By.XPATH, ".//input[@class='J_input_val']"
        #加入购物车按钮
        self.add_cart_btn = By.XPATH, ".//a[text()='加入购物车']"
        # 商品详情链接（用于跳转到详情页）- 在 context 内查找第一个 a 标签
        self.item_link = By.XPATH, ".//div[contains(@class,'goods-img') or contains(@class,'title')]//a[1]"
    
    # 在 context 容器内查找（而不是整个页面）
    def context_find_element(self, loc, timeout=10):
        """在商品项容器内查找元素"""
        return WebDriverWait(self.driver, timeout).until(
            lambda x: self.context.find_element(*loc)
        )

    # 设置购买数量
    def set_buy_num(self, num):
        # 等待输入框可见后再操作
        num_ele = self.context_find_element(self.num_input)
        num_ele.clear()
        num_ele.send_keys(str(num))

    # 点击加入购物车
    def click_add_cart(self):
        # 等待按钮可点击后再点击
        btn = self.context_find_element(self.add_cart_btn)
        btn.click()
    
    # 点击整个商品项（跳转到详情页）
    def click_item(self):
        """点击商品项的详情链接，用于跳转到商品详情页"""
        # 在商品项容器内查找详情链接并点击
        try:
            # 尝试查找商品详情链接（优先使用通用选择器）
            link = self.context_find_element(self.item_link)
            link.click()
        except Exception as e:
            print(f"→ 常规点击失败：{str(e)}，尝试使用 JS 点击...")
            # 如果找不到特定的链接，尝试点击 context 内的第一个 a 标签
            try:
                first_link = self.context.find_element(By.TAG_NAME, 'a')
                self.driver.execute_script("arguments[0].click();", first_link)
            except:
                # 最后方案：直接点击 context（某些网站可能有效）
                self.driver.execute_script("arguments[0].click();", self.context)

class PageSearch(BasePage):
    """搜索页面配置"""

    # 搜索框
    search_input = By.CSS_SELECTOR, ".ecsc-search-input"

    # 搜索按钮
    search_btn = By.CSS_SELECTOR, ".ecsc-search-button"

    # 商品列表容器
    goods_list = By.XPATH, "//div[4]/div/div[2]/div[2]"

    # 购物车内商品数量 (角标)
    cart_nums = By.CSS_SELECTOR, ".shop-nums"

    #加入成功提示框关闭按钮
    close_add_success = By.CSS_SELECTOR, "#layui-layer1 > span > a"

    """筛选项"""
    # 价格筛选
    # 起始价
    start_price = By.CSS_SELECTOR, "input[name='start_price']"
    # 结束价
    end_price = By.CSS_SELECTOR, "input[name='end_price']"
    # 价格筛选确定按钮
    price_confirm = By.XPATH, "//*[@id='price_form']/input[3]"
    # 清空筛选条件
    clear_filter = By.PARTIAL_LINK_TEXT, "清空筛选条件"

    """结果排序"""
    # 综合
    sort_default = By.PARTIAL_LINK_TEXT, "综合"
    # 销量
    sort_sales = By.PARTIAL_LINK_TEXT, "销量"
    # 价格 (第一次点击价格：低->高，再次点击翻转)
    sort_price = By.PARTIAL_LINK_TEXT, "价格"
    # 评论
    sort_comment = By.PARTIAL_LINK_TEXT, "评论"
    # 新品
    sort_new = By.PARTIAL_LINK_TEXT, "新品"

    def page_input_search(self, key):
        """输入搜索关键词"""
        self.base_input(self.search_input, key)

    def page_click_search_btn(self):
        """点击搜索按钮"""
        self.base_click(self.search_btn)

    def page_enter_search(self):
        """回车触发搜索"""
        self.base_input(self.search_input, Keys.ENTER)

    def page_get_url(self):
        """获取当前页面 URL"""
        return self.driver.current_url

    def page_get_screenshot(self):
        """截图"""
        return self.base_get_screenshot()

    def page_get_item_by_position(self, position):
        """
        按位置获取商品项
        position = 1 → 第 1 个商品
        position = 2 → 第 2 个商品
        完全和页面看到的一样！
        """
        # 等待商品列表容器可见
        list_container = self.base_find_visible_element(self.goods_list)
        # 定位第 position 个 li，即 第 position 个商品
        item_xpath = f"./ul/li[{position}]/div"
        single_item_ele = list_container.find_element(By.XPATH, item_xpath)
        # 返回商品组件对象（需传入 driver 和元素）
        return GoodsItem(self.driver, single_item_ele)

    def page_add_item_to_cart_by_position(self, position=1, buy_num=1):
        """封装统一「指定位置 + 数量 加购」"""
        item = self.page_get_item_by_position(position)
        item.set_buy_num(buy_num)
        item.click_add_cart()

    #关闭成功加入提示框
    def page_close_add_success(self):
        self.base_click(self.close_add_success)

    def page_get_cart_num(self):
        """获取购物车角标数量"""
        return self.base_get_text(self.cart_nums)

    def page_search_and_click_item(self, key, position):
        """
        基础搜索
        Args:
            key: 搜索关键词
            position: 商品位置
        """
        self.page_input_search(key)
        self.page_click_search_btn()
        self.page_get_item_by_position(position).click_item()


