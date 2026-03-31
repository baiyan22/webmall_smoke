"""
定位器管理器 - 集中管理所有页面元素定位器
支持从 YAML 配置文件动态加载定位器
"""
import yaml
from pathlib import Path
from selenium.webdriver.common.by import By


class LocatorManager:
    """定位器管理器单例"""
    
    def __init__(self):
        self._cache = {}
    
    def load_locators(self, yaml_file: str, page_key: str = None) -> dict:
        """
        从 YAML 文件加载定位器
        
        :param yaml_file: YAML 文件路径
        :param page_key: YAML 中的页面键名（如 'cart_page'）
        :return: 定位器字典
        """
        cache_key = f"{yaml_file}:{page_key}"
        
        # 检查缓存
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # 加载 YAML 文件
        yaml_path = Path(yaml_file)
        if not yaml_path.is_absolute():
            # 使用绝对路径，避免 pytest 相对路径陷阱
            yaml_path = Path(__file__).parent.parent / "locators" / yaml_file
        
        with open(yaml_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # 如果指定了 page_key，只返回该页面的定位器
        if page_key and page_key in config:
            locators = config[page_key]
        else:
            locators = config
        
        # 缓存结果
        self._cache[cache_key] = locators
        return locators
    
    def get_locator_tuple(self, locator_dict: dict) -> tuple:
        """
        将定位器字典转换为 Selenium By 元组
        
        :param locator_dict: {'by': 'css', 'value': '.checkall'}
        :return: (By.CSS_SELECTOR, '.checkall')
        """
        by_mapping = {
            'css': By.CSS_SELECTOR,
            'xpath': By.XPATH,
            'id': By.ID,
            'name': By.NAME,
            'class_name': By.CLASS_NAME,
            'link_text': By.LINK_TEXT,
            'partial_link_text': By.PARTIAL_LINK_TEXT,
            'tag_name': By.TAG_NAME,
        }
        
        by_type = locator_dict.get('by', 'css').lower()
        value = locator_dict.get('value', '')
        
        if by_type not in by_mapping:
            raise ValueError(f"不支持的定位类型：{by_type}")
        
        return by_mapping[by_type], value


# 全局单例
locator_manager = LocatorManager()
