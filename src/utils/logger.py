"""日志工具：同时输出日志到控制台和文件，按日期保存"""
import logging
import os
from datetime import datetime

# 日志目录：项目根目录下的logs文件夹（自动创建）
log_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs"
)
os.makedirs(log_dir, exist_ok=True)  # 若目录不存在则创建

# 日志文件：按日期命名（如20240520.log）
log_file = os.path.join(log_dir, f"{datetime.now().strftime('%Y%m%d')}.log")

# 配置日志格式：时间-日志名-级别-内容
logging.basicConfig(
    level=logging.INFO,  # 日志级别：INFO及以上才会输出
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),  # 输出到文件
        logging.StreamHandler()  # 输出到控制台
    ]
)

# 创建日志实例，供其他模块调用
logger = logging.getLogger("auto_test")