"""接口请求执行器：封装requests，自动处理会话和token
提供统一的接口请求方法，简化用例中的请求发送逻辑
"""
import requests
from src.utils.logger import logger
from src.utils.var_handler import get_var  # 用于获取全局token


class ApiRunner:
    def __init__(self, base_url: str, timeout: int = 10):
        """初始化执行器
        Args:
            base_url: 接口基础URL（如"https://t.rcwzsh.com:9999"）
            timeout: 超时时间（秒）
        """
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()  # 创建会话，保持cookie等状态

    def run(self, api_config: dict) -> requests.Response:
        """执行接口请求
        Args:
            api_config: 接口配置字典，包含method/path等信息
        Returns:
            接口响应对象
        """
        # 解析接口配置
        method = api_config.get("method", "get").lower()  # 请求方法（默认get）
        path = api_config.get("path")  # 接口路径（如"/api/order/create"）
        params = api_config.get("params", {})  # URL参数
        json_data = api_config.get("json", {})  # JSON请求体
        data = api_config.get("data", {})  # 表单请求体
        headers = api_config.get("headers", {})  # 请求头

        # 自动添加token到请求头（若存在全局token）
        token = get_var("global.token")
        if token:
            # 按接口要求的格式添加（此处为示例，需根据实际接口调整）
            headers["x-oiltax-token"] = token
            logger.info("已自动添加token到请求头")

        # 校验路径是否存在
        if not path:
            raise ValueError("接口配置缺少必要的'path'（路径）参数")

        # 拼接完整URL
        full_url = self.base_url + path
        logger.info(f"【请求】{method.upper()} {full_url}")  # 打印请求方法和URL
        logger.debug(f"请求参数: params={params}, json={json_data}")  # 调试日志

        try:
            # 发送请求
            response = self.session.request(
                method=method,
                url=full_url,
                params=params,
                json=json_data,
                data=data,
                headers=headers,
                timeout=self.timeout
            )
            logger.info(f"【响应】状态码: {response.status_code}")  # 打印响应状态码
            return response
        except Exception as e:
            logger.error(f"请求执行失败: {str(e)}")
            raise  # 抛出异常，让用例捕获