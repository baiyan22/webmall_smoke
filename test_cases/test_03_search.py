import pytest
from utils.log_utils import GetLogger
from pages.page_search import PageSearch
from utils.yaml_utils import read_yaml
import os
import allure
import time

# 读取配置
config = read_yaml(os.path.join(os.path.dirname(__file__), '../config/config.yaml'))

# 读取测试数据
test_data = read_yaml(os.path.join(os.path.dirname(__file__), '../test_data/search_data.yaml'))

# 日志实例化
logger = GetLogger().get_logger()

class TestSearch:
    """搜索功能测试类"""

    driver=None
    page_search=None

    @pytest.fixture(autouse=True)
    def setup(self, logged_in):
        """确保测试处于登录状态"""
        self.driver = logged_in
        self.page_search = PageSearch(logged_in)

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
        if key == "test_search_fail":
            data_list = test_data['test_search_fail']
        else:
            data_list = test_data['test_search_success']
            
        for case in data_list:
            if case['name'] == case_name:
                return case
        raise ValueError(f"未找到测试用例：{case_name}")
    
    def _execute_search_test(self, case):
        """
        执行搜索测试的通用方法
        Args:
            case: 测试用例数据
        """
        # 打开搜索页面（假设从首页开始）
        with allure.step("打开首页"):
            self.page_search.open_url("https://hmshop-test.itheima.net/home/Index/index.html")

        # 获取购物车初始数量
        cart_initial_num = self.page_search.page_get_cart_num()
            
        # 遍历所有搜索关键词（支持多个）
        for i, search_item in enumerate(case['data']):
            # 输入搜索关键词
            with allure.step(f"输入搜索关键词：{search_item['key']}"):
                self.page_search.page_input_search(search_item['key'])
                
            # 点击搜索按钮
            with allure.step("点击搜索按钮"):
                self.page_search.page_click_search_btn()
                
            # 等待搜索结果加载
            time.sleep(5)
                
            # 验证搜索后的 URL（优先使用 YAML 配置的 URL，否则动态生成）
            current_url = self.page_search.page_get_url()
            # 如果 YAML 中有对应索引的 URL 则使用，否则根据关键词动态生成
            if len(case['expected']) > i and 'url' in case['expected'][i]:
                expected_url = case['expected'][i]['url']
            else:
                from urllib.parse import quote
                expected_url = f"https://hmshop-test.itheima.net/Home/Goods/search.html?q={quote(search_item['key'])}"
                
            with allure.step(f"验证搜索后 URL"):
                assert current_url == expected_url, f"搜索后 URL 不正确：期望{expected_url}, 实际{current_url}"
                
            # 选择商品加入购物车
            position = search_item['position']
            buy_num = search_item['num']
                
            with allure.step(f"选择第{position}个商品，数量{buy_num}，加入购物车"):
                self.page_search.page_add_item_to_cart_by_position(position, buy_num)
                self.page_search.page_close_add_success()
            
        # 验证购物车总数量
        cart_final_num = self.page_search.page_get_cart_num()
        #商品增加总数量（需要转换为整数后计算）
        cart_num = str(int(cart_final_num) - int(cart_initial_num))

        expected_sum = str(case['expected'][0]['sum'])
            
        with allure.step(f"验证这次购物中，购物车中增加的商品总数量：期望{expected_sum}, 实际{cart_num}"):
            assert cart_num == expected_sum, f"购物车中增加的商品总数量不正确：期望{expected_sum}, 实际{cart_num}"
            
        # 截图保存
        with allure.step("截图保存"):
            screenshot = self.page_search.page_get_screenshot()
            if screenshot:
                allure.attach(
                    screenshot,
                    name="搜索结果页面截图",
                    attachment_type=allure.attachment_type.PNG
                )
            
        print(f"✓ 搜索测试通过：{case['name']}")

    @allure.feature("搜索功能")
    @allure.story("成功场景测试")
    @pytest.mark.smoke  # 冒烟测试标记
    @pytest.mark.parametrize("case_name", [
        pytest.param(test_data['test_search_success'][0]['name'], id="search_success_smoke"),
    ])
    def test_search_success_smoke(self, case_name):
        """
        搜索成功 - 冒烟测试（只测第一个核心流程）
        执行策略：只执行 YAML 中的第一个测试用例
        """
        # 获取测试数据
        case = self._get_case_data(case_name, key="test_search_success")
        
        allure.dynamic.title(f"搜索测试 - {case_name}（冒烟）")
        allure.dynamic.description(f"测试场景：{case_name}")
        allure.dynamic.severity(allure.severity_level.BLOCKER)
        
        # 执行测试
        self._execute_search_test(case)

    @allure.feature("搜索功能")
    @allure.story("成功场景测试")
    @pytest.mark.parametrize("case_name", 
        [pytest.param(case['name'], id=f"search_{i}") for i, case in enumerate(test_data['test_search_success'])]
    )
    def test_search_success_full(self, case_name):
        """
        搜索成功 - 完整测试（测试所有成功场景）
        执行策略：执行 YAML 中定义的所有测试用例
        """
        # 获取测试数据
        case = self._get_case_data(case_name, key="test_search_success")
        
        allure.dynamic.title(f"搜索测试 - {case_name}（完整）")
        allure.dynamic.description(f"测试场景：{case_name}")
        allure.dynamic.severity(allure.severity_level.CRITICAL)
        
        # 执行测试
        self._execute_search_test(case)

    @allure.feature("搜索功能")
    @allure.story("异常场景测试")
    @pytest.mark.parametrize("case_name", [
        pytest.param("无结果关键词搜索", id="no_result"),
        pytest.param("空关键词搜索", id="empty_keyword"),
    ])
    def test_search_failures(self, case_name):
        """
        搜索失败/异常场景测试
        """
        # 获取测试数据
        case = self._get_case_data(case_name, key="test_search_fail")
        
        allure.dynamic.title(f"搜索测试 - {case_name}")
        allure.dynamic.description(f"测试场景：{case_name}")
        allure.dynamic.severity(allure.severity_level.NORMAL)
        
        # 打开搜索页面
        with allure.step("打开首页"):
            self.page_search.open_url("https://hmshop-test.itheima.net/home/Index/index.html")
        
        # 输入搜索关键词
        with allure.step(f"输入搜索关键词：{case['data']}"):
            self.page_search.page_input_search(case['data'])
        
        # 触发搜索
        with allure.step(f"触发搜索方式：{case['trigger']}"):
            if case['trigger'] == 'btn':
                self.page_search.page_click_search_btn()
            elif case['trigger'] == 'enter':
                self.page_search.page_enter_search()
        
        # 等待搜索结果加载
        time.sleep(2)
        
        # 验证错误信息（如果有）
        if 'msg' in case['expected'][0]:
            with allure.step("验证错误提示"):
                # TODO: 根据实际页面的错误提示来实现
                pass
        
        # 截图保存
        with allure.step("截图保存"):
            screenshot = self.page_search.base_get_screenshot()
            if screenshot:
                allure.attach(
                    screenshot,
                    name="搜索异常页面截图",
                    attachment_type=allure.attachment_type.PNG
                )
        
        print(f"✓ 搜索异常测试完成：{case_name}")