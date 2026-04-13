"""
规则映射 - 11类数据实践 → 12类违规类型
仅用于A版本
"""
import torch

# CAPP-130 11类数据实践
CAPP130_LABELS = [
    "First Party Collection",      # 0: 信息收集
    "Permission Acquisition",      # 1: 权限获取
    "Third Party Sharing",         # 2: 第三方共享
    "Usage",                       # 3: 使用方式
    "Data Retention",              # 4: 数据留存
    "Data Security",               # 5: 数据安全
    "Specific Audiences",          # 6: 特定用户
    "Edit/Control",                # 7: 编辑控制
    "Contact Information",         # 8: 联系方式
    "Policy Change",               # 9: 政策变更
    "Cease Operation",             # 10: 停止运营
]

# 12类违规类型
VIOLATION_LABELS = [
    "I1-过度收集敏感数据",
    "I2-未明示目的",
    "I3-未获得明示同意",
    "I4-收集范围超出需求",
    "I5-第三方范围不明",
    "I6-未获得单独授权",
    "I7-未提供删除",
    "I8-未提供注销",
    "I9-未提供查询",
    "I10-未明确权利范围",
    "I11-未提供便捷途径",
    "I12-其他违规",
]

def map_to_violations(probs_11: torch.Tensor, threshold: float = 0.3) -> dict:
    """
    11类数据实践概率 → 12类违规风险
    
    Args:
        probs_11: 11类概率tensor
        threshold: 风险阈值
    
    Returns:
        dict: {违规类型: 风险值}
    """
    probs = probs_11[0].cpu()
    violations = {}
    
    # 映射规则（基于业务逻辑）
    
    # I1-过度收集敏感数据: 信息收集 + 判断"过度"
    violations["I1"] = probs[0].item() * 0.8  # 权重0.8
    
    # I2-未明示目的: 使用方式 + 信息收集
    violations["I2"] = max(probs[3].item(), probs[0].item() * 0.5)
    
    # I3-未获得明示同意: 权限获取
    violations["I3"] = probs[1].item()
    
    # I4-收集范围超出需求: 信息收集 + 判断"超出"
    violations["I4"] = probs[0].item() * 0.6
    
    # I5-第三方范围不明: 第三方共享
    violations["I5"] = probs[2].item()
    
    # I6-未获得单独授权: 第三方共享 + 判断"单独"
    violations["I6"] = probs[2].item() * 0.7
    
    # I7-I11: 编辑控制相关
    edit_control_prob = probs[7].item()
    violations["I7"] = edit_control_prob * 0.8
    violations["I8"] = edit_control_prob * 0.7
    violations["I9"] = edit_control_prob * 0.6
    violations["I10"] = edit_control_prob * 0.9
    violations["I11"] = edit_control_prob * 0.5
    
    # I12-其他违规: 取所有类别的最大值
    violations["I12"] = max(probs.max().item() * 0.3, 0.1)
    
    return violations

def format_violation_result(violations: dict, threshold: float = 0.3) -> str:
    """
    格式化违规结果输出
    
    Args:
        violations: 违规风险字典
        threshold: 显示阈值
    
    Returns:
        str: 格式化的结果字符串
    """
    result = "## 违规风险分析\n\n"
    
    # 按风险值排序
    sorted_violations = sorted(violations.items(), key=lambda x: x[1], reverse=True)
    
    # 高风险
    high_risk = [(k, v) for k, v in sorted_violations if v >= threshold]
    if high_risk:
        result += "### ⚠️ 高风险项\n"
        for label, prob in high_risk:
            idx = int(label[1:]) - 1
            result += f"- **{VIOLATION_LABELS[idx]}**: {prob:.1%}\n"
    
    # 低风险
    low_risk = [(k, v) for k, v in sorted_violations if v < threshold]
    if low_risk:
        result += "\n### ✓ 低风险项\n"
        for label, prob in low_risk:
            idx = int(label[1:]) - 1
            result += f"- {VIOLATION_LABELS[idx]}: {prob:.1%}\n"
    
    return result

def get_capp130_explanation(capp_idx: int) -> str:
    """获取CAPP-130类别解释"""
    explanations = {
        0: "涉及用户信息的收集方式、目的及影响",
        1: "涉及应用权限的获取方式及授权说明",
        2: "涉及与第三方共享或披露用户信息",
        3: "涉及用户数据的使用方式和目的",
        4: "涉及用户信息的存储期限和位置",
        5: "涉及数据安全保护措施",
        6: "涉及特定用户群体的特殊条款",
        7: "涉及用户对数据的编辑和控制权利",
        8: "涉及联系方式和反馈渠道",
        9: "涉及隐私政策的变更通知",
        10: "涉及服务停止运营后的数据处理",
    }
    return explanations.get(capp_idx, "")
