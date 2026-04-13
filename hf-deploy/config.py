"""
版本配置 - A/B版本切换
"""
import os

# 从环境变量读取版本，默认A
VERSION = os.getenv("APP_VERSION", "A")

# A版配置：CAPP-130（11类数据实践）
A_CONFIG = {
    "version": "A",
    "model_name": "CAPP-130",
    "repo_id": "sybululu/bert-moe",
    "classifier_file": "multi_classification_bertmoe.ckpt",
    "num_labels": 11,
    "base_model": "bert-base-chinese",
    "labels": [
        "信息收集", "权限获取", "第三方共享", "使用方式", "数据留存",
        "数据安全", "特定用户", "编辑控制", "联系方式", "政策变更", "停止运营"
    ],
    "description": "CAPP-130数据实践分类（11类）"
}

# B版配置：自定义模型（12类违规）- 预留接口
B_CONFIG = {
    "version": "B",
    "model_name": "Custom-12",
    "repo_id": "sybululu/bert-moe",  # 临时用同一个，之后替换
    "classifier_file": "your_custom_model.ckpt",  # TODO: 替换为自己的模型
    "num_labels": 12,
    "base_model": "bert-base-chinese",
    "labels": [
        "I1-过度收集敏感数据", "I2-未明示目的", "I3-未获得明示同意", 
        "I4-收集范围超出需求", "I5-第三方范围不明", "I6-未获得单独授权",
        "I7-未提供删除", "I8-未提供注销", "I9-未提供查询",
        "I10-未明确权利范围", "I11-未提供便捷途径", "I12-其他违规"
    ],
    "description": "自定义12类违规识别（预留接口）"
}

def get_config():
    """获取当前版本配置"""
    return A_CONFIG if VERSION == "A" else B_CONFIG

def get_version_info():
    """获取版本信息字符串"""
    config = get_config()
    return f"版本 {config['version']}: {config['model_name']} - {config['description']}"
