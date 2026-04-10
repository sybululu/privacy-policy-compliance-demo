"""
数据模型定义
基于浙大CAPP-130的12项违规指示符
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class RiskLevel(str, Enum):
    """风险等级枚举"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Violation(BaseModel):
    """违规条款模型"""
    id: str = Field(..., description="违规编号 (I1-I12)")
    type: str = Field(..., description="违规类型名称")
    original_text: str = Field(..., description="违规原文")
    law_article: str = Field(..., description="对应法律条款")
    suggestion: str = Field(..., description="整改建议")
    confidence: float = Field(..., description="置信度 0-1", ge=0, le=1)
    risk_category: str = Field(..., description="风险类别")


class AnalysisRequest(BaseModel):
    """分析请求模型"""
    text: str = Field(..., description="隐私政策文本", min_length=10)


class AnalysisResponse(BaseModel):
    """分析响应模型"""
    score: int = Field(..., ge=0, le=100, description="合规评分 0-100")
    risk_level: RiskLevel = Field(..., description="风险等级")
    total_indicators: int = Field(default=12, description="总检查指标数")
    passed_indicators: int = Field(default=0, description="通过指标数")
    violations: List[Violation] = Field(default_factory=list, description="违规条款列表")
    analysis_details: dict = Field(default_factory=dict, description="分析详情")


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = "ok"
    message: str = "Privacy Policy Analyzer is running"
    model_info: dict = Field(default_factory=dict, description="模型信息")


# 12项合规指标定义 (CAPP-130 Dataset)
COMPLIANCE_INDICATORS = {
    "I1": {
        "type": "收集范围超出必要",
        "category": "Information Collection",
        "law_article": "《个人信息保护法》第六条",
        "description": "收集个人信息的范围应当限于实现处理目的的最小必要范围"
    },
    "I2": {
        "type": "未明确收集目的",
        "category": "Information Collection",
        "law_article": "《个人信息保护法》第十七条",
        "description": "处理个人信息应当具有明确、合理的目的"
    },
    "I3": {
        "type": "未获得用户同意",
        "category": "Authorization and Revisions",
        "law_article": "《个人信息保护法》第十四条",
        "description": "基于个人同意处理个人信息的，应当取得个人的同意"
    },
    "I4": {
        "type": "收集敏感信息未单独告知",
        "category": "Information Collection",
        "law_article": "《个人信息保护法》第二十九条",
        "description": "处理敏感个人信息应当取得个人的单独同意"
    },
    "I5": {
        "type": "共享第三方未告知",
        "category": "Sharing and Disclosure",
        "law_article": "《个人信息保护法》第二十三条",
        "description": "向第三方提供个人信息应当向个人告知接收方等信息"
    },
    "I6": {
        "type": "共享第三方未获同意",
        "category": "Sharing and Disclosure",
        "law_article": "《个人信息保护法》第二十三条",
        "description": "向第三方提供个人信息应当取得个人的单独同意"
    },
    "I7": {
        "type": "留存期限不合理",
        "category": "Storage",
        "law_article": "《个人信息保护法》第十九条",
        "description": "个人信息的保存期限应当为实现处理目的所必要的最短时间"
    },
    "I8": {
        "type": "未明确留存期限",
        "category": "Storage",
        "law_article": "《个人信息保护法》第十九条",
        "description": "应当明确标注个人信息的存储期限"
    },
    "I9": {
        "type": "未提供删除途径",
        "category": "Management",
        "law_article": "《个人信息保护法》第五十条",
        "description": "个人有权请求删除其个人信息"
    },
    "I10": {
        "type": "未明确权利范围",
        "category": "Management",
        "law_article": "《个人信息保护法》第四十四条至第五十条",
        "description": "应当明确告知个人享有的各项权利"
    },
    "I11": {
        "type": "未提供便捷途径",
        "category": "Management",
        "law_article": "《个人信息保护法》第五十条",
        "description": "应当提供便捷的个人信息处理请求渠道"
    },
    "I12": {
        "type": "未明确响应时限",
        "category": "Management",
        "law_article": "《个人信息保护法》第五十条",
        "description": "对个人请求的响应应当在规定时限内完成"
    }
}

# 整改建议模板
REMEDIATION_SUGGESTIONS = {
    "I1": "明确界定个人信息收集的具体范围，删除非必要的收集项目。建议逐一列举收集的信息类型，并说明每类信息的收集必要性。",
    "I2": "清晰、明确地说明收集每类个人信息的目的，采用具体表述替代模糊表述。避免使用'其他合法目的'等含糊措辞。",
    "I3": "建立明示同意机制，移除默认同意选项。在收集敏感信息前必须获取用户的明确、单独同意。",
    "I4": "对于生物识别、医疗健康、金融账户等敏感信息，应当单独显著提示并获取单独同意。",
    "I5": "详细披露与第三方共享个人信息的情况，包括接收方名称、处理目的、共享信息类型等。",
    "I6": "在向第三方提供个人信息前，必须获得用户的单独明示同意，不得捆绑一揽子授权。",
    "I7": "根据法律要求和业务需要设定合理的数据留存期限，避免过度存储。超过必要期限后应主动删除。",
    "I8": "在隐私政策中明确标注各类个人信息的具体存储期限，说明确定期限的依据。",
    "I9": "提供便捷的个人信息删除渠道，如在线自助删除、客服申请等方式。说明删除后的数据处理情况。",
    "I10": "详细列明用户享有的查阅、复制、更正、删除等各项权利，并说明行使方式。",
    "I11": "提供简便易用的个人信息管理入口，如在线客服、专用表单、邮箱等申诉渠道。",
    "I12": "明确个人信息请求的响应时限，如15个工作日内完成，并在隐私政策中予以说明。"
}
