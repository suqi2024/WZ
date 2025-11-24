"""全局变量处理工具：读写user_vars.yaml中的用户信息和全局变量
支持多级路径访问（如"user.username"、"global.token"）
"""
import yaml
import os

def get_var(key_path: str):
    """读取变量值
    Args:
        key_path: 变量路径（如"global.token"）
    Returns:
        变量值（若不存在返回None）
    """
    # 变量文件路径：config/user_vars.yaml
    file_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "config", "user_vars.yaml"
    )
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"变量文件不存在：{file_path}")

    # 读取YAML文件
    with open(file_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}  # 若文件为空则返回空字典

    # 解析多级路径（如"global.token"拆分为["global", "token"]）
    keys = key_path.split(".")
    value = data
    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            return None  # 路径不存在时返回None
    return value


def set_var(key_path: str, value):
    """设置变量值（会覆盖原有值）
    Args:
        key_path: 变量路径（如"global.token"）
        value: 要设置的值
    """
    file_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "config", "user_vars.yaml"
    )
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"变量文件不存在：{file_path}")

    # 读取原有数据
    with open(file_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    # 解析路径并设置值
    keys = key_path.split(".")
    current = data
    # 处理除最后一个键之外的路径（确保中间层级存在）
    for k in keys[:-1]:
        if k not in current or not isinstance(current[k], dict):
            current[k] = {}  # 若不存在则创建字典
        current = current[k]
    # 设置最终值
    current[keys[-1]] = value

    # 写回文件（保留中文，不排序键）
    with open(file_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)