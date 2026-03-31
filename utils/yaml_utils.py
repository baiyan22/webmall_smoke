import yaml
import os

def read_yaml(yaml_path):
    """读取YAML文件"""
    with open(yaml_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    return data

def get_test_data(file_name):
    """获取测试数据"""
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', file_name)
    return read_yaml(path)