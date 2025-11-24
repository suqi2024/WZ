"""YAML用例数据读取工具：读取data目录下的用例数据文件
支持YAML多文档格式，返回用例列表
"""
import yaml
import os
from typing import List, Dict


class DataReader:
    @staticmethod
    def read_yaml(file_path: str) -> List[Dict]:
        """读取YAML文件并返回用例列表
        Args:
            file_path: YAML文件路径（如"data/order_cases.yaml"）
        Returns:
            用例列表（每个元素为一个用例字典）
        """
        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"用例文件不存在: {file_path}")

        # 读取YAML文件（支持多文档）
        with open(file_path, "r", encoding="utf-8") as f:
            # safe_load_all返回生成器，转换为列表
            cases = list(yaml.safe_load_all(f))
            # 处理单文档情况（若文件只有一个文档，外层加列表）
            if len(cases) == 1 and isinstance(cases[0], list):
                return cases[0]
            return cases