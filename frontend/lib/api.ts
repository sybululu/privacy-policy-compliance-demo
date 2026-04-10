// API 类型定义

export type RiskLevel = 'high' | 'medium' | 'low'

export interface Violation {
  id: string
  type: string
  original_text: string
  law_article: string
  suggestion: string
  confidence: number
  risk_category: string
}

export interface AnalysisResponse {
  score: number
  risk_level: RiskLevel
  total_indicators: number
  passed_indicators: number
  violations: Violation[]
  analysis_details: {
    sentences_analyzed: number
    model_source: string
    risk_model: string
    rewrite_model: string
    detection_results: Record<string, number>
  }
}

export interface AnalysisRequest {
  text: string
}

// API 调用函数
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export async function analyzePolicy(text: string): Promise<AnalysisResponse> {
  const response = await fetch(`${API_BASE_URL}/api/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ text }),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || '分析失败')
  }

  return response.json()
}

export async function getSample(): Promise<{ sample: string }> {
  const response = await fetch(`${API_BASE_URL}/api/sample`)
  
  if (!response.ok) {
    throw new Error('获取示例失败')
  }

  return response.json()
}

export async function getIndicators(): Promise<{
  total: number
  indicators: Array<{
    id: string
    type: string
    category: string
    law_article: string
    description: string
  }>
}> {
  const response = await fetch(`${API_BASE_URL}/api/indicators`)
  
  if (!response.ok) {
    throw new Error('获取指标列表失败')
  }

  return response.json()
}
