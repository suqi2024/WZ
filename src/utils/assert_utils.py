"""断言工具类：封装常用的断言方法，简化用例中的断言逻辑
支持响应状态码断言、JSON字段断言等
"""
import jsonpath
from src.utils.logger import logger
import requests


class AssertUtils:
    @staticmethod
    def assert_code(response: requests.Response, expected_code: int):
        """断言响应状态码
        Args:
            response: 接口响应对象
            expected_code: 预期状态码（如200）
        """
        actual_code = response.status_code
        assert actual_code == expected_code, \
            f"状态码断言失败: 预期{expected_code}, 实际{actual_code}"
        logger.info(f"状态码断言通过（预期{expected_code}，实际{actual_code}）")

    @staticmethod
    def assert_json(response: requests.Response, json_path: str, expected_value):
        """用JSONPath断言响应中的字段值
        Args:
            response: 接口响应对象
            json_path: JSONPath表达式（如"$.data.order_id"）
            expected_value: 预期值
        """
        try:
            # 解析响应JSON并提取字段值
            actual_value = jsonpath.jsonpath(response.json(), json_path)[0]
            # 执行断言
            assert actual_value == expected_value, \
                f"JSON字段断言失败: 路径{json_path}，预期{expected_value}，实际{actual_value}"
            logger.info(f"JSON字段断言通过：{json_path} = {expected_value}")
        except IndexError:
            # JSONPath未找到匹配结果
            raise AssertionError(f"JSONPath路径不存在或无匹配值：{json_path}")
        except TypeError:
            # 响应不是JSON格式
            raise AssertionError(f"响应无法解析为JSON，无法执行断言：{json_path}")