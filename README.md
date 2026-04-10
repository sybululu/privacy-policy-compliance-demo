# 隐私政策合规审查Demo

基于浙大CAPP-130的隐私政策合规性分析工具，界面设计灵感来自Claude.ai。

## 项目概述

本项目使用浙江大学CAPP-130数据集训练的AI模型，对隐私政策进行合规性审查：

- **风险识别模型**: RoBERTa/PERT（Risk-Micro F1 = 92.0%）
- **整改建议生成**: 中文增强版mT5（IDEA-CCNL/mT5-base-chinese-cluecorpussmall，中文任务提升3.2%）

## 功能特性

- 📋 **隐私政策分析**: 快速识别隐私政策中的潜在违规条款
- 🎯 **合规评分**: 0-100分直观的合规评分
- ⚠️ **风险等级**: 高/中/低三级风险评估
- 📝 **违规详情**: 列出具体违规条款及对应法条
- 💡 **mT5整改建议**: 基于浙大微调mT5生成的专业整改方案

## 12项合规检查指标

| 编号 | 指标 | 涉及法规 |
|------|------|----------|
| I1 | 收集范围超出必要 | 个人信息保护法第6条 |
| I2 | 未明确收集目的 | 个人信息保护法第17条 |
| I3 | 未获得用户同意 | 个人信息保护法第14条 |
| I4 | 收集敏感信息未单独告知 | 个人信息保护法第29条 |
| I5 | 共享第三方未告知 | 个人信息保护法第23条 |
| I6 | 共享第三方未获同意 | 个人信息保护法第23条 |
| I7 | 留存期限不合理 | 个人信息保护法第19条 |
| I8 | 未明确留存期限 | 个人信息保护法第19条 |
| I9 | 未提供删除途径 | 个人信息保护法第50条 |
| I10 | 未明确权利范围 | 个人信息保护法第44-50条 |
| I11 | 未提供便捷途径 | 个人信息保护法第50条 |
| I12 | 未明确响应时限 | 个人信息保护法第50条 |

## 快速启动

### 方式一：Docker Compose（推荐）

```bash
# 克隆项目
git clone <repository-url>
cd 隐私政策合规审查Demo

# 构建并启动所有服务
docker-compose up --build

# 访问应用
# 前端: http://localhost:3000
# 后端API: http://localhost:8000
# API文档: http://localhost:8000/docs
```

### 方式二：手动启动

#### 后端

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn main:app --reload --port 8000
```

#### 前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 或构建生产版本
npm run build
npm start
```

## 项目结构

```
隐私政策合规审查Demo/
├── frontend/                 # Next.js 14 前端应用
│   ├── app/                  # App Router
│   │   ├── layout.tsx       # 根布局
│   │   ├── page.tsx        # 主页面
│   │   └── globals.css     # 全局样式
│   ├── lib/                 # 工具函数和API
│   │   ├── utils.ts       # 工具函数
│   │   └── api.ts         # API调用
│   ├── Dockerfile          # Docker配置
│   └── package.json        # 依赖配置
├── backend/                 # FastAPI 后端服务
│   ├── main.py            # 应用入口
│   ├── models.py          # 数据模型
│   ├── analyzer.py        # CAPP-130分析器
│   ├── requirements.txt   # Python依赖
│   └── Dockerfile         # Docker配置
├── CAPP-130/              # 浙大CAPP-130数据集（Git submodule）
├── docker-compose.yml     # Docker编排配置
└── README.md             # 项目说明
```

## API 接口

### POST /api/analyze

分析隐私政策文本。

**请求体：**
```json
{
  "text": "隐私政策文本内容..."
}
```

**响应：**
```json
{
  "score": 75,
  "risk_level": "medium",
  "total_indicators": 12,
  "passed_indicators": 8,
  "violations": [
    {
      "id": "I1",
      "type": "收集范围超出必要",
      "original_text": "我们收集您的所有信息...",
      "law_article": "《个人信息保护法》第六条",
      "suggestion": "明确界定个人信息收集的具体范围...",
      "confidence": 0.85,
      "risk_category": "Information Collection"
    }
  ],
  "analysis_details": {
    "sentences_analyzed": 45,
    "model_source": "EnlightenedAI/TCSI_pp_zh",
    "risk_model": "RoBERTa/PERT (Risk F1=92.0%)",
    "rewrite_model": "mT5 (ROUGE-L=0.733)"
  }
}
```

### GET /api/indicators

获取12项合规检查指标的详细信息。

### GET /api/sample

获取示例隐私政策文本。

## 模型说明

### CAPP-130 简介

CAPP-130（Chinese Application Privacy Policy Summarization and Interpretation）是浙江大学发布的中文隐私政策数据集，包含：

- 130篇中文应用隐私政策
- 52,489条标注
- 20,555条改写后的句子

### TCSI-pp 框架

本项目使用的TCSI-pp框架包括：

1. **风险识别模型**：使用RoBERTa或PERT进行二分类（风险/非风险）
   - RoBERTa Risk-Micro F1: 92.0%
   - PERT Risk-Micro F1: 92.2%

2. **整改建议生成**：使用微调后的mT5模型
   - ROUGE-1: 0.753
   - ROUGE-2: 0.609
   - ROUGE-L: 0.733

### 模型来源

- 论文：https://openreview.net/forum?id=OyTIV57Prb
- GitHub：https://github.com/EnlightenedAI/CAPP-130
- HuggingFace：https://huggingface.co/EnlightenedAI/TCSI_pp_zh

## 技术栈

- **前端**：Next.js 14 + Tailwind CSS + TypeScript
- **后端**：FastAPI + Pydantic + Python
- **AI模型**：Transformers + PyTorch
- **容器化**：Docker + docker-compose

## 开发说明

### 模型加载

首次启动时，后端会自动从HuggingFace下载预训练模型：

```bash
# 模型将保存到 backend/models/ 目录
python download_models.py
```

### 本地模型替换

如需使用本地模型：

1. 下载浙大TCSI_pp_zh模型到 `backend/models/` 目录
2. 修改 `backend/analyzer.py` 中的模型路径
3. 重启后端服务

## License

MIT License

## Citation

```bibtex
@inproceedings{zhu2023capp,
  title={CAPP-130: a corpus of chinese application privacy policy summarization and interpretation},
  author={Zhu, Pengyun and Wen, Long and Liu, Jinfei and Xue, Feng and Lou, Jian and Wang, Zhibo and Ren, Kui},
  booktitle={Proceedings of the 37th International Conference on Neural Information Processing Systems},
  pages={46773--46785},
  year={2023}
}
```
