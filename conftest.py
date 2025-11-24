"""pytest全局配置：定义fixture、钩子函数等
fixture是pytest的核心功能，用于提供测试依赖（如接口执行器）
"""
import pytest
import yaml
import time
from src.utils.api_runner import ApiRunner
from src.utils.logger import logger


def pytest_collection_modifyitems(items):
    """钩子函数：收集完用例后，按指定顺序排序模块"""
    # 1. 定义你需要的模块执行顺序（先 user → 后 order，登录仍优先）
    module_order = [
        'test_login.py',  # 登录永远第一
        'test_user.py',  # 用户模块第二
        'test_order.py'  # 订单模块第三
    ]

    # 2. 按模块名排序用例
    import os
    def get_module_name(item):
        """获取用例所在的模块文件名（如 test_user.py）"""
        return os.path.basename(item.module.__file__)

    # 3. 排序逻辑：按 module_order 中的索引排序，未指定的模块放最后
    items.sort(
        key=lambda item: module_order.index(get_module_name(item))
        if get_module_name(item) in module_order else 999
    )


# 读取环境配置（从config/config.yaml）
with open("config/config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

# @pytest.fixture(scope="session", autouse=True)
# def add_timestamp_metadata(metadata):
#     """
#     在测试会话开始时，自动添加当前时间戳到 metadata 中。
#     """
#     current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
#     metadata["执行时间"] = current_time
#     yield
#     # 夹具结束时无需操作

@pytest.fixture(scope="session")
def api_runner():
    """全局接口执行器（会话级别：整个测试过程只初始化一次）
    所有用例共享此执行器，保持会话状态
    """
    # 获取测试环境配置（可切换为prod）
    env_config = config["env"]["test"]
    # 初始化ApiRunner
    runner = ApiRunner(
        base_url=env_config["base_url"],
        timeout=env_config.get("timeout", 10)
    )
    logger.info(f"接口执行器初始化完成，基础URL：{env_config['base_url']}")
    yield runner  # 提供执行器给用例使用
    # 测试结束后清理（如关闭会话）
    runner.session.close()
    logger.info("接口执行器已关闭会话")


def pytest_sessionstart(session):
    """测试会话开始时执行：打印开始日志"""
    logger.info("\n=============== 自动化测试会话开始 ===============")


def pytest_sessionfinish(session, exitstatus):
    """测试会话结束时执行：打印结束日志"""
    logger.info("\n=============== 自动化测试会话结束 ===============\n")