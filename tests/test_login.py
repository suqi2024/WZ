"""登录模块用例：负责获取token并保存到全局变量
所有其他模块的用例依赖此模块生成的token
"""
import jsonpath
import pytest
from src.utils.logger import logger
from src.utils.var_handler import get_var, set_var
from src.utils.assert_utils import AssertUtils


@pytest.mark.api
#@pytest.mark.order(1)  # 标记为第一个执行（优先级最高）
def test_login(api_runner):
    """登录接口测试：获取token和user_id并保存到全局变量"""
    logger.info("=============== 开始执行登录用例 ===============")

    # 1. 从配置文件读取登录信息
    username = get_var("user.username")  # 读取用户手机号
    sms_code = get_var("user.smsCode")   # 读取验证码
    if not username or not sms_code:
        raise ValueError("请在config/user_vars.yaml中配置user.username和user.smsCode")

    # 2. 登录接口配置（根据实际接口调整）
    login_config = {
        "method": "post",
        "path": "/api/customer/person/login/user",  # 登录接口路径
        "json": {
            "mobile": username,       # 手机号
            "smsCode": sms_code       # 验证码
        }
    }

    # 3. 发送登录请求
    response = api_runner.run(login_config)


    # 4. 断言登录成功
    AssertUtils.assert_code(response, 200)  # 断言HTTP状态码为200
    # 可根据实际响应添加更多断言（如业务码）
    AssertUtils.assert_json(response, "$.code", "0000")  # 示例：断言业务码为0000

    # 5. 提取token并保存到全局变量
    token_path = "$.data.token"  # token在响应中的JSONPath（根据实际响应调整）
    token_list = jsonpath.jsonpath(response.json(), token_path)
    if token_list and len(token_list) > 0:
        token = token_list[0]
        set_var("global.token", token)  # 保存到global.token
        logger.info(f"登录成功，已提取并保存token：{token[:10]}...")  # 隐藏部分字符
    else:
        raise AssertionError(f"未从响应中提取到token（JSONPath：{token_path}）")

    # 6. 提取user_id并保存（可选，供其他接口使用）
    user_id_path = "$.data.userId"  # user_id的JSONPath（根据实际响应调整）
    user_id_list = jsonpath.jsonpath(response.json(), user_id_path)
    if user_id_list and len(user_id_list) > 0:
        user_id = user_id_list[0]
        set_var("global.user_id", user_id)  # 保存到global.user_id
        logger.info(f"已提取并保存user_id：{user_id}")

    logger.info("=============== 登录用例执行完毕 ===============")