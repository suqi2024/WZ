# 抽取所有模块用例的公共逻辑，避免冗余
from src.utils.var_manager import get_var, set_var
from src.utils.logger import logger

class TestBase:
    @staticmethod
    def handle_api_config(api_config):
        """公共逻辑：处理请求配置（变量替换+携带token）"""
        # 1. 替换变量（如 ${token}）
        if "json" in api_config:
            for k, v in api_config["json"].items():
                if isinstance(v, str) and v.startswith("${") and v.endswith("}"):
                    var_name = v[2:-1]
                    api_config["json"][k] = get_var(f"global.{var_name}")
                    logger.info(f"替换变量：{k} = ${var_name} → {api_config['json'][k]}")
        # 2. 携带登录token
        token = get_var("global.token")
        if token:
            api_config.setdefault("headers", {})["token"] = token
            logger.info(f"携带token：{token[:10]}...")
        else:
            raise ValueError("未获取到登录token，无法执行业务用例！")
        return api_config

    @staticmethod
    def extract_variables(response, extract_config):
        """公共逻辑：提取变量并保存到全局"""
        if not extract_config:
            return
        from jsonpath import jsonpath
        for var_name, json_path in extract_config.items():
            value_list = jsonpath(response.json(), json_path)
            if value_list and len(value_list) > 0:
                set_var(f"global.{var_name}", value_list[0])
                logger.info(f"提取变量成功：{var_name} = {value_list[0]}")
            else:
                logger.warning(f"提取变量失败：{var_name}（JSONPath：{json_path}）")