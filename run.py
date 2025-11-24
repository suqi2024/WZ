"""测试执行入口：可直接运行此文件执行所有用例
也可通过命令行参数指定执行特定模块
"""
import pytest
import os
#import subprocess

if __name__ == "__main__":
    # 执行所有用例并生成报告（默认）
    # pytest.main(["--html=report/all_report.html"])

    # 执行指定模块（示例：只执行订单模块）
     #pytest.main(["tests/test_user.py", "--html=report/user_report.html"])
     #pytest.main(["tests/test_order.py", "--html=report/order_report.html"])

# 执行所有用例（使用pytest.ini中的配置）
    pytest.main()

# ################################html的报告##################
#     # 确保报告目录存在
# # 定义报告目录和路径
#     # 定义报告目录和路径
#     report_dir = "report"
#     report_path = os.path.join(report_dir, "test_report.html")
#
#     # 确保报告目录存在
#     if not os.path.exists(report_dir):
#         os.makedirs(report_dir)
#
#     # 执行测试，生成HTML报告（使用默认模板）
#     pytest.main([
#         "tests/",  # 指定要运行的测试目录
#         "-v",  # 详细输出模式
#         f"--html={report_path}",  # 生成HTML报告，并指定报告路径
#         "--self-contained-html"  # (可选) 将所有CSS和JS嵌入到单个HTML文件中，方便分享
#     ])
#
#     print(f"\n测试报告已生成：{os.path.abspath(report_path)}")