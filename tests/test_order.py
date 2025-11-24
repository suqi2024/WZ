"""订单模块用例：依赖登录模块的token，可单独执行或批量执行
包含创建订单、查询订单等用例，用例数据保存在data/order_cases.yaml
"""
import pytest
import jsonpath
from src.utils.logger import logger
from src.utils.read_data import DataReader
from src.utils.var_handler import get_var, set_var
from src.utils.assert_utils import AssertUtils


# 读取订单模块用例数据（从data/order_cases.yaml）
order_cases = DataReader.read_yaml("data/order_cases.yaml")


@pytest.mark.api
#@pytest.mark.order(2)  # 确保在登录之后执行（数字越大越靠后）
class TestOrder:
    """订单模块测试类：所有订单相关用例在此类中"""

    def setup_class(self):
        """模块初始化：执行整个订单模块用例前的准备工作"""
        # 检查全局token是否存在
        self.token = get_var("global.token")
        if not self.token:
            # 若不存在，提示用户先执行登录用例或手动配置token
            raise ValueError(
                "全局token不存在！请先执行登录用例（test_login.py）"
                "或在config/user_vars.yaml中手动配置global.token"
            )
        logger.info("订单模块初始化完成，token验证通过")

    @pytest.mark.parametrize(
        "case",  # 用例参数名
        order_cases,  # 用例数据列表
        # 用例ID：在报告中显示，便于定位
        ids=[case.get("case_id", f"order_case_{idx}") for idx, case in enumerate(order_cases)]
    )
    def test_order(self, api_runner, case):
        """执行订单模块用例：支持变量替换、响应提取、断言"""
        logger.info(f"=============== 执行用例: {case['case_id']} - {case['title']} ===============")

        # 1. 复制用例配置（避免修改原数据）
        api_config = case["api"].copy()

        # 2. 替换请求参数中的变量引用（如${user_id}）
        # 2.1 处理JSON请求体中的变量
        if "json" in api_config:
            for key, value in api_config["json"].items():
                # 识别变量格式：${变量名}
                if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                    var_name = value[2:-1]  # 提取变量名（如"user_id"）
                    # 从全局变量获取值并替换
                    var_value = get_var(f"global.{var_name}")
                    if var_value is not None:
                        api_config["json"][key] = var_value
                        logger.info(f"已替换JSON参数变量：{key} = {var_value}")
                    else:
                        logger.warning(f"未找到全局变量：{var_name}，将使用原始值")

        # 2.2 处理URL参数中的变量（如params中的${order_id}）
        if "params" in api_config:
            for key, value in api_config["params"].items():
                if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                    var_name = value[2:-1]
                    var_value = get_var(f"global.{var_name}")
                    if var_value is not None:
                        api_config["params"][key] = var_value
                        logger.info(f"已替换URL参数变量：{key} = {var_value}")

        # 3. 发送接口请求（api_runner会自动携带token）
        response = api_runner.run(api_config)
        logger.info(f"接口响应: {response.json()}")  # 打印响应内容

        # 4. 提取响应中的变量（供后续用例使用）
        if "extract" in case:
            for var_name, json_path in case["extract"].items():
                # 用JSONPath提取值
                value_list = jsonpath.jsonpath(response.json(), json_path)
                if value_list and len(value_list) > 0:
                    extracted_value = value_list[0]
                    # 保存到全局变量（如global.order_id）
                    set_var(f"global.{var_name}", extracted_value)
                    logger.info(f"已提取变量：{var_name} = {extracted_value}")
                else:
                    logger.warning(f"变量提取失败：{var_name}（JSONPath：{json_path}）")

        # 5. 替换断言中的变量引用（如预期结果中的${order_id}）
        expected = case["expected"].copy()  # 复制预期结果，避免修改原数据
        if "json" in expected:
            for json_path, exp_val in expected["json"].items():
                if isinstance(exp_val, str) and exp_val.startswith("${") and exp_val.endswith("}"):
                    var_name = exp_val[2:-1]
                    var_value = get_var(f"global.{var_name}")
                    if var_value is not None:
                        expected["json"][json_path] = var_value
                        logger.info(f"已替换断言变量：{json_path} = {var_value}")

        # 6. 执行断言
        AssertUtils.assert_code(response, expected["code"])  # 断言状态码
        # 断言JSON字段
        if "json" in expected:
            for json_path, exp_val in expected["json"].items():
                AssertUtils.assert_json(response, f"$.{json_path}", exp_val)

        logger.info(f"=============== 用例: {case['case_id']} 执行完毕 ===============\n")