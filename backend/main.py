"""
隐私政策合规审查后端服务
基于浙大CAPP-130模型

浙大论文: CAPP-130: A Corpus of Chinese Application Privacy Policy Summarization and Interpretation
GitHub: https://github.com/EnlightenedAI/CAPP-130
HuggingFace: https://huggingface.co/EnlightenedAI/TCSI_pp_zh
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from models import AnalysisRequest, AnalysisResponse, HealthResponse, RiskLevel
from analyzer import analyzer

# 创建 FastAPI 应用
app = FastAPI(
    title="隐私政策合规审查API",
    description="""
    ## 基于浙大CAPP-130的隐私政策合规审查服务
    
    使用浙大TCSI-pp框架进行隐私政策合规性分析：
    - **风险识别模型**: RoBERTa/PERT (Risk-Micro F1 = 92.0%)
    - **整改建议生成**: mT5 (ROUGE-L = 0.733)
    
    ### 12项合规检查指标 (CAPP-130)
    1. I1: 收集范围超出必要
    2. I2: 未明确收集目的
    3. I3: 未获得用户同意
    4. I4: 收集敏感信息未单独告知
    5. I5: 共享第三方未告知
    6. I6: 共享第三方未获同意
    7. I7: 留存期限不合理
    8. I8: 未明确留存期限
    9. I9: 未提供删除途径
    10. I10: 未明确权利范围
    11. I11: 未提供便捷途径
    12. I12: 未明确响应时限
    
    ### 模型来源
    - 论文: https://openreview.net/forum?id=OyTIV57Prb
    - GitHub: https://github.com/EnlightenedAI/CAPP-130
    - HuggingFace: https://huggingface.co/EnlightenedAI/TCSI_pp_zh
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=HealthResponse)
async def root():
    """健康检查端点"""
    return HealthResponse(
        status="ok", 
        message="隐私政策合规审查服务运行中",
        model_info={
            "source": "Zhejiang University CAPP-130",
            "risk_model": "RoBERTa/PERT (F1=92.0%)",
            "rewrite_model": "mT5 (ROUGE-L=0.733)",
            "github": "https://github.com/EnlightenedAI/CAPP-130"
        }
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查端点"""
    return HealthResponse(
        status="ok", 
        message="服务正常运行",
        model_info={
            "source": "Zhejiang University CAPP-130",
            "risk_model": "RoBERTa/PERT (F1=92.0%)",
            "rewrite_model": "mT5 (ROUGE-L=0.733)"
        }
    )


@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_policy(request: AnalysisRequest):
    """
    分析隐私政策文本
    
    使用浙大CAPP-130模型分析输入的隐私政策文本，识别其中的违规条款，
    并提供合规评分和基于mT5生成的整改建议。
    
    ### 请求体
    - **text**: 隐私政策文本内容（至少10个字符）
    
    ### 响应
    - **score**: 合规评分（0-100分）
    - **risk_level**: 风险等级（high/medium/low）
    - **violations**: 违规条款列表（包含置信度和mT5生成的整改建议）
    """
    try:
        # 验证输入
        if not request.text or len(request.text.strip()) < 10:
            raise HTTPException(
                status_code=400,
                detail="隐私政策文本内容过短，至少需要10个字符"
            )
        
        # 执行分析
        result = analyzer.analyze(request.text)
        
        # 转换为响应模型
        response = AnalysisResponse(
            score=result["score"],
            risk_level=RiskLevel(result["risk_level"]),
            total_indicators=result["total_indicators"],
            passed_indicators=result["passed_indicators"],
            violations=result["violations"],
            analysis_details=result["analysis_details"]
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"分析过程发生错误: {str(e)}"
        )


@app.get("/api/indicators")
async def get_indicators():
    """
    获取所有合规检查指标信息
    
    返回CAPP-130的12项合规检查指标的详细信息。
    """
    from models import COMPLIANCE_INDICATORS
    
    indicators_list = []
    for indicator_id, info in COMPLIANCE_INDICATORS.items():
        indicators_list.append({
            "id": indicator_id,
            "type": info["type"],
            "category": info.get("category", ""),
            "law_article": info["law_article"],
            "description": info["description"]
        })
    
    return {
        "total": len(indicators_list),
        "source": "Zhejiang University CAPP-130",
        "paper": "https://openreview.net/forum?id=OyTIV57Prb",
        "indicators": indicators_list
    }


# 示例隐私政策文本
SAMPLE_PRIVACY_POLICY = """
[示例隐私政策 - 仅供测试使用]

我们非常重视您的个人信息和隐私保护。以下是本应用的隐私政策：

一、信息收集
1. 我们收集您在使用服务时主动提供的信息，包括姓名、邮箱、手机号码等。
2. 我们收集您的所有浏览记录、位置信息和通讯录，以便为您提供个性化服务。
3. 您的信息可能被用于我们认为合适的其他合法目的。

二、Cookie使用
我们使用Cookie追踪您的浏览行为以优化广告投放效果。

三、第三方共享
我们可能与广告合作伙伴和第三方服务商共享您的个人信息，无需额外通知。

四、数据保留
您的数据将被永久保存在我们的服务器上，只要您继续使用我们的服务。

五、账户注销
您的账户无法被注销，一旦注册即表示同意永久保留账户信息。删除账户信息需要联系客服，且可能收取一定费用。

六、儿童隐私
我们的服务面向包括14岁以下儿童在内的用户群体。

七、跨境传输
您的数据将被传输至境外数据中心进行存储。

八、数据安全
虽然我们尽力保护您的信息安全，但对于数据泄露我们不承担任何责任。

九、用户权利
用户无法自行删除或更正已提交的个人信息。如需行使权利，请联系我们的客服团队。
"""


@app.get("/api/sample")
async def get_sample():
    """获取示例隐私政策文本"""
    return {
        "sample": SAMPLE_PRIVACY_POLICY,
        "note": "此示例包含多种常见违规条款，可用于测试系统功能"
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
