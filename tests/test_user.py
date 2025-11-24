"""用户模块用例：依赖登录模块的token，支持单独执行
包含查询用户信息、修改用户资料等用例，数据保存在data/user_cases.yaml
"""
import pytest
import jsonpath
from src.utils.logger import logger
from src.utils.read_data import DataReader
from src.utils.var_handler import get_var, set_var
from src.utils.assert_utils import AssertUtils


# 读取用户模块用例数据
user_cases = DataReader.read_yaml("data/user_cases.yaml")


@pytest.mark.api
#@pytest.mark.order(3)  # 执行顺序：登录(1) → 订单(2) → 用户(3)
class TestUser:
    """用户模块测试类"""

    def setup_class(self):
        """模块初始化：检查token是否存在"""
        self.token = get_var("global.token")
        if not self.token:
            raise ValueError(
                "全局token不存在！请先执行登录用例（test_login.py）"
                "或在config/user_vars.yaml中手动配置global.token"
            )
        logger.info("用户模块初始化完成，token验证通过")

    @pytest.mark.parametrize(
        "case",
        user_cases,
        ids=[case.get("case_id", f"user_case_{idx}") for idx, case in enumerate(user_cases)]
    )
    def test_user(self, api_runner, case):
        """执行用户模块用例"""
        logger.info(f"=============== 执行用例: {case['case_id']} - {case['title']} ===============")

        # 1. 复制用例配置（避免污染原数据）
        api_config = case["api"].copy()

        # 2. 替换请求参数中的变量（如${user_id}）
        if "json" in api_config:
            for key, value in api_config["json"].items():
                if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                    var_name = value[2:-1]
                    var_value = get_var(f"global.{var_name}")
                    if var_value is not None:
                        api_config["json"][key] = var_value
                        logger.info(f"替换JSON参数变量：{key} = {var_value}")

        if "params" in api_config:
            for key, value in api_config["params"].items():
                if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                    var_name = value[2:-1]
                    var_value = get_var(f"global.{var_name}")
                    if var_value is not None:
                        api_config["params"][key] = var_value
                        logger.info(f"替换URL参数变量：{key} = {var_value}")

        # 3. 发送请求（自动携带token）
        response = api_runner.run(api_config)
        logger.info(f"接口响应: {response.json()}")

        # 4. 提取变量（供后续用例）
        if "extract" in case:
            for var_name, json_path in case["extract"].items():
                value_list = jsonpath.jsonpath(response.json(), json_path)
                if value_list and len(value_list) > 0:
                    set_var(f"global.{var_name}", value_list[0])
                    logger.info(f"提取变量：{var_name} = {value_list[0]}")

        # 5. 替换断言中的变量
        expected = case["expected"].copy()
        if "json" in expected:
            for json_path, exp_val in expected["json"].items():
                if isinstance(exp_val, str) and exp_val.startswith("${") and exp_val.endswith("}"):
                    var_name = exp_val[2:-1]
                    expected["json"][json_path] = get_var(f"global.{var_name}")

        # 6. 执行断言
        AssertUtils.assert_code(response, expected["code"])
        if "json" in expected:
            for json_path, exp_val in expected["json"].items():
                AssertUtils.assert_json(response, f"$.{json_path}", exp_val)

        logger.info(f"=============== 用例: {case['case_id']} 执行完毕 ===============\n")