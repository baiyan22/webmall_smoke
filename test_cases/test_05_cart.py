from pages.page_cart import PageCart
import pytest
from utils.log_utils import GetLogger
from utils.yaml_utils import read_yaml
import os
import allure
import time

# 读取配置
config = read_yaml(os.path.join(os.path.dirname(__file__), '../config/config.yaml'))

# 读取测试数据
test_data = read_yaml(os.path.join(os.path.dirname(__file__), '../test_data/cart_data.yaml'))

class TestCart:
    """购物车测试类"""
    driver = None
    page_cart = None

    @pytest.fixture(autouse=True)
    def setup(self, logged_in):
        """确保测试处于登录状态"""
        self.driver = logged_in
        self.page_cart = PageCart(logged_in)

    # 获取测试数据
    def _get_case_data(self, case_name, key):
        """
        根据用例名称获取测试数据
        Args:
            case_name: 用例名称
            key: YAML 中的 key 对象，用于分别成功、失败场景
        Returns: dict: 测试数据
        """
        # 根据类型选择对应的数据列表
        if key == "test_cart_success":
            data_list = test_data['test_cart_success']
        else:
            data_list = test_data['test_cart_fail']

        for case in data_list:
            if case['name'] == case_name:
                return case
        raise ValueError(f"未找到测试用例：{case_name}")

    def _execute_cart_test(self, case, time=None):
        """
        执行商品详情页测试的通用方法
        Args:
            case: 测试用例数据
        """
        # 打开搜索页面（假设从首页开始）
        with allure.step("打开首页"):
            self.page_cart.open_url("https://hmshop-test.itheima.net/home/Index/index.html")

        # 进入购物车
        with allure.step("点击购物车"):
            self.page_cart.page_click_cart()
        
        # 取消所有勾选（确保总价只计算我们要测试的商品）
        with allure.step("取消所有勾选"):
            # 先检查是否有全选按钮，如果有且处于选中状态，则点击取消
            try:
                import time
                time.sleep(1)  # 等待购物车页面完全加载
                
                # 直接定位到隐藏的 input 元素，使用 is_selected() 判断
                all_select_checkbox = self.page_cart.base_find_element(self.page_cart.all_select_btn)
                is_checked = all_select_checkbox.is_selected()
                
                GetLogger().get_logger().info(f"全选按钮当前状态：{'已勾选' if is_checked else '未勾选'}")
                
                if is_checked:
                    GetLogger().get_logger().info("检测到全选状态，正在取消...")
                    self.page_cart.page_all_select_click()
                    time.sleep(1)  # 等待页面刷新
                    GetLogger().get_logger().info("已取消所有商品的勾选")
                    
                    # 关键：刷新页面确保价格重新计算
                    GetLogger().get_logger().info("→ 刷新页面以确保价格同步...")
                    self.driver.refresh()
                    time.sleep(2)  # 等待页面完全刷新
                    GetLogger().get_logger().info("✓ 页面刷新完成")
                else:
                    GetLogger().get_logger().info("商品未处于全选状态")
            except Exception as e:
                error_msg = str(e)
                GetLogger().get_logger().warning(f"检查全选按钮时发生异常：{error_msg}")
                GetLogger().get_logger().info("继续执行后续步骤（可能无全选按钮或无需取消）")

        total_price = 0

        # 遍历所有测试商品项（支持多个）
        for i, item in enumerate(case['data']):
            position = item['position']
            good_num = item['good_num']
            
            # 获取订单项对象并复用
            cart_item = self.page_cart.get_cart_item(position)
            
            # 先取消勾选，再重新勾选（确保状态正确）
            with allure.step(
                    f"勾选中购物车中第 {position} 个商品，并修改购买数量为{good_num}"):
                
                # 关键步骤：先修改数量，再重新勾选（触发页面刷新）
                # 1. 如果商品已勾选，先取消
                if cart_item.item_is_selected():
                    cart_item.item_unselect()
                    GetLogger().get_logger().info(f"第 {position} 个商品已取消勾选")
                    import time
                    time.sleep(0.3)
                
                # 2. 修改数量（此时不勾选，不会计入总价）
                cart_item.item_set_num(good_num)
                GetLogger().get_logger().info(f"第 {position} 个商品数量已修改为 {good_num}")
                
                # 3. 等待数量修改生效和价格刷新
                import time
                time.sleep(1.5)  # 增加等待时间让价格刷新

                # 4. 勾选商品（触发前端事件，更新总价）
                cart_item.item_select()
                GetLogger().get_logger().info(f"第 {position} 个商品已勾选")
                
                # 关键：等待价格重新计算
                import time
                time.sleep(2)  # 增加到 2 秒，确保价格完全刷新
                
                # 5. 验证是否成功勾选（确保状态正确）
                if not cart_item.item_is_selected():
                    # 如果没勾选上，再次尝试
                    GetLogger().get_logger().warning(f"第 {position} 个商品首次勾选失败，重试...")
                    cart_item.item_select()
                    time.sleep(1)

                    # 再次验证
                    current_status = cart_item.item_is_selected()
                    GetLogger().get_logger().info(f"第 {position} 个商品当前勾选状态：{current_status}")

                    if not current_status:
                        error_msg = f"❌ 第 {position} 个商品勾选失败！当前状态：{current_status}"
                        GetLogger().get_logger().error(error_msg)
                        raise AssertionError(error_msg)
                    else:
                        GetLogger().get_logger().info(f"✓ 第 {position} 个商品重试勾选成功")
                
            # 获取单价
            with allure.step(f"获取第 {position} 个商品的单价："):
                # 再次确认商品处于勾选状态
                if not cart_item.item_is_selected():
                    GetLogger().get_logger().error(f"⚠️ 警告：第 {position} 个商品在获取单价时未勾选！")
                    cart_item.item_select()
                    time.sleep(0.5)
                
                price = cart_item.item_get_single_price()
                GetLogger().get_logger().info(f"商品单价为：{price}")
            
            # 累加期望总价
            total_price += price * good_num
            GetLogger().get_logger().info(f"当前累计期望总价：{total_price}")

            
        with allure.step(f"获取结算总价格："):
            total_price_actual = self.page_cart.page_get_total_price()
            GetLogger().get_logger().info(f"结算总价格为：{total_price_actual}")
            
        # 验证总价（允许浮点数精度误差）
        assert abs(total_price - total_price_actual) < 0.01, \
            f"购物车结算总价格不匹配：期望{total_price:.2f}, 实际{total_price_actual:.2f}"

        # 截图保存
        with allure.step("截图保存"):
            screenshot = self.page_cart.page_get_screenshot()
            if screenshot:
                allure.attach(
                    screenshot,
                    name="购物车结果页面截图",
                    attachment_type=allure.attachment_type.PNG
                )

        print(f"✓ 购物车页测试通过：{case['name']}")

    @allure.feature("购物车功能")
    @allure.story("成功场景测试")
    @pytest.mark.smoke  # 冒烟测试标记
    @pytest.mark.parametrize("case_name", [
        pytest.param(test_data['test_cart_success'][0]['name'], id="cart_success_smoke"),
    ])
    def test_cart_success_smoke(self, case_name):
        """
        购物车页操作成功 - 冒烟测试（只测第一个核心流程）
        执行策略：只执行 YAML 中的第一个测试用例
        """
        # 获取测试数据
        case = self._get_case_data(case_name, key="test_cart_success")

        allure.dynamic.title(f"购物车页测试 - {case_name}（冒烟）")
        allure.dynamic.description(f"测试场景：{case_name}")
        allure.dynamic.severity(allure.severity_level.BLOCKER)

        # 执行测试
        self._execute_cart_test(case)