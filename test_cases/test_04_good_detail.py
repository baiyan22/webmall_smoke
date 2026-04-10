from pages.page_good_detail import PageGoodDetail
import pytest
from utils.log_utils import GetLogger
from utils.yaml_utils import read_yaml
import os
import allure
import time

# 读取配置
config = read_yaml(os.path.join(os.path.dirname(__file__), '../config/config.yaml'))

# 读取测试数据
test_data = read_yaml(os.path.join(os.path.dirname(__file__), '../test_data/good_detail_data.yaml'))

# 日志实例化
logger = GetLogger().get_logger()

class TestGoodDetail:
    """商品详情页测试类"""
    driver = None
    page_good_detail = None

    @pytest.fixture(autouse=True)
    def setup(self, logged_in):
        """确保测试处于登录状态"""
        self.driver = logged_in
        self.page_good_detail= PageGoodDetail(logged_in)

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
        if key == "test_good_detail_success":
            data_list = test_data['test_good_detail_success']
        else:
            data_list = test_data['test_good_detail_fail']

        for case in data_list:
            if case['name'] == case_name:
                return case
        raise ValueError(f"未找到测试用例：{case_name}")
    
    def _execute_good_detail_test(self, case):
        """
        执行商品详情页测试的通用方法
        Args:
            case: 测试用例数据
        """
        # 打开搜索页面（假设从首页开始）
        with allure.step("打开首页"):
            self.page_good_detail.open_url("https://hmshop-test.itheima.net/home/Index/index.html")

        # 获取购物车初始数量
        cart_initial_num = self.page_good_detail.page_get_cart_num()

        # 遍历所有搜索关键词（支持多个）
        for i, search_item in enumerate(case['data']):
            # 输入搜索关键词
            with allure.step(f"输入搜索关键词：{search_item['key']}并点击搜索结果的第{search_item['good_position']}个商品，"):
                # 记录点击前的 URL
                url_before = self.page_good_detail.page_get_url()
                # 执行搜索并点击商品
                self.page_good_detail.page_search_and_click_item(key=search_item['key'],good_position=search_item['good_position'])

                # 等待商品详情页加载（使用 URL 变化判断）
            with allure.step("⏳ 等待商品详情页加载（URL 变化检测）"):
                try:
                    from selenium.webdriver.support.ui import WebDriverWait
                    from selenium.webdriver.support import expected_conditions as EC
                    
                    # 等待 URL 发生变化（从搜索页跳转到商品详情页）
                    WebDriverWait(self.driver, 15).until(
                        lambda d: d.current_url != url_before
                    )
                    logger.info("✓ 检测到 URL 已变化，商品详情页已加载完成")
                    logger.info(f"  → 新 URL: {self.page_good_detail.page_get_url()}")
                except Exception as e:
                    logger.error(f"⚠ 等待商品详情页超时：{str(e)}")
                    # 保存调试截图
                    screenshot = self.driver.get_screenshot_as_png()
                    allure.attach(
                        screenshot,
                        name="商品详情页加载失败截图",
                        attachment_type=allure.attachment_type.PNG
                    )
                    raise

            with allure.step(f"📍 点击配送地址：省份：{search_item['province_position']}，市级：{search_item['city_position']}，区县：{search_item['area_position']}"):
                # 使用元组解包接收三个返回值
                addr = self.page_good_detail.page_input_and_get_address(
                    search_item['province_position'], 
                    search_item['city_position'], 
                    search_item['area_position']
                )
                province_text, city_text, area_text = addr
                
                # 在日志中打印
                logger.info(f"✓ 选择的配送地址：{province_text} {city_text} {area_text}")
                
                # 在 Allure 报告中附加详细信息
                allure.attach(
                    f"省份：{province_text}\n城市：{city_text}\n区县：{area_text}",
                    name="配送地址详情",
                    attachment_type=allure.attachment_type.TEXT
                )

            with allure.step(f"🔢 设置购买数量为：{case['data'][i]['num']}"):
                self.page_good_detail.page_input_num(search_item['num'])

            with allure.step(f"🛒 购物方式选择：{case['data'][i]['buy_type']}"):
                if case['data'][i]['buy_type'] == 'cart':
                    logger.info("选择加入购物车")
                    #加入购物车并成功后关闭提示框
                    self.page_good_detail.page_add_cart()
                    time.sleep(3)
                    self.page_good_detail.page_close_add_success()
                    logger.info("✓ 已成功加入购物车")
                else:
                    logger.info("选择立即购买（暂未实现）")
                    self.page_good_detail.page_buy_now()
                    time.sleep(5)
                    """
                    此区域还未实现
                    """
                    pass





        # 验证购物车总数量
        cart_final_num = self.page_good_detail.page_get_cart_num()
        # 商品增加总数量（需要转换为整数后计算）
        cart_num = str(int(cart_final_num) - int(cart_initial_num))

        expected_sum = str(case['expected'][0]['sum'])

        with allure.step(f"✅ 验证购物车增加数量：期望{expected_sum}, 实际{cart_num}"):
            assert cart_num == expected_sum, f"购物车中增加的商品总数量不正确：期望{expected_sum}, 实际{cart_num}"

        # 截图保存
        with allure.step("📸 截图保存"):
            screenshot = self.page_good_detail.page_get_screenshot()
            if screenshot:
                allure.attach(
                    screenshot,
                    name="商品详情结果页面截图",
                    attachment_type=allure.attachment_type.PNG
                )

        logger.info(f"✓ 商品详情页测试通过：{case['name']}")

    @allure.feature("商品详情功能")
    @allure.story("成功场景测试")
    @pytest.mark.smoke  # 冒烟测试标记
    @pytest.mark.parametrize("case_name", [
        pytest.param(test_data['test_good_detail_success'][0]['name'], id="good_detail_success_smoke"),
    ])
    def test_good_detail_success_smoke(self, case_name):
        """
        商品详情页操作成功 - 冒烟测试（只测第一个核心流程）
        执行策略：只执行 YAML 中的第一个测试用例
        """
        # 获取测试数据
        case = self._get_case_data(case_name, key="test_good_detail_success")

        allure.dynamic.title(f"🛍️ 商品详情功能 - {case_name}（冒烟测试）")
        allure.dynamic.description(
            f"**测试场景**: {case_name}\n\n"
            f"**测试目标**:\n"
            f"- 验证搜索并进入商品详情页\n"
            f"- 验证配送地址选择功能\n"
            f"- 验证商品数量设置\n"
            f"- 验证加入购物车功能\n"
            f"- 验证购物车数量计算准确\n\n"
            f"**预期结果**: 商品成功加入购物车，购物车数量增加 {case['expected'][0]['sum']} 件"
        )
        allure.dynamic.severity(allure.severity_level.BLOCKER)
        allure.dynamic.tag("smoke", "good_detail", "add_to_cart")
        
        # 添加测试数据附件
        with allure.step("📋 测试数据"):
            test_info = ""
            for i, item in enumerate(case['data']):
                test_info += f"商品{i+1}:\n"
                test_info += f"  - 关键词: {item['key']}\n"
                test_info += f"  - 位置: {item['good_position']}\n"
                test_info += f"  - 数量: {item['num']}\n"
                test_info += f"  - 配送地址: 省{item['province_position']}/市{item['city_position']}/区{item['area_position']}\n"
                test_info += f"  - 购买方式: {item['buy_type']}\n\n"
            
            allure.attach(
                test_info,
                name="测试数据详情",
                attachment_type=allure.attachment_type.TEXT
            )

        # 执行测试
        logger.info(f"开始执行商品详情冒烟测试: {case_name}")
        self._execute_good_detail_test(case)
        logger.info(f"✓ 商品详情冒烟测试通过: {case_name}")
        
