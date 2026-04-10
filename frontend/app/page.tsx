'use client'

import { useState, useEffect } from 'react'
import { 
  Shield, 
  AlertTriangle, 
  CheckCircle, 
  ChevronDown, 
  ChevronUp,
  Loader2,
  Trash2,
  FileText,
  Sparkles,
  Info
} from 'lucide-react'
import { cn, getProgressRingProps, getRiskLevelColor, formatConfidence } from '@/lib/utils'
import { analyzePolicy, getSample, type AnalysisResponse, type Violation } from '@/lib/api'

export default function Home() {
  const [inputText, setInputText] = useState('')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [result, setResult] = useState<AnalysisResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [expandedViolations, setExpandedViolations] = useState<Set<string>>(new Set())

  // 加载示例
  const loadSample = async () => {
    try {
      const { sample } = await getSample()
      setInputText(sample)
    } catch (e) {
      console.error('加载示例失败:', e)
    }
  }

  // 清空输入
  const clearInput = () => {
    setInputText('')
    setResult(null)
    setError(null)
  }

  // 分析政策
  const handleAnalyze = async () => {
    if (!inputText.trim() || inputText.length < 10) {
      setError('请输入至少10个字符的隐私政策文本')
      return
    }

    setIsAnalyzing(true)
    setError(null)
    setResult(null)

    try {
      const analysisResult = await analyzePolicy(inputText)
      setResult(analysisResult)
      // 默认展开前3个违规
      const firstThree = new Set(
        analysisResult.violations.slice(0, 3).map(v => v.id)
      )
      setExpandedViolations(firstThree)
    } catch (e: any) {
      setError(e.message || '分析失败，请稍后重试')
    } finally {
      setIsAnalyzing(false)
    }
  }

  // 切换违规展开状态
  const toggleViolation = (id: string) => {
    setExpandedViolations(prev => {
      const newSet = new Set(prev)
      if (newSet.has(id)) {
        newSet.delete(id)
      } else {
        newSet.add(id)
      }
      return newSet
    })
  }

  const { circumference, offset, color } = getProgressRingProps(result?.score || 0)

  return (
    <div className="min-h-screen bg-claude-bg">
      {/* Header */}
      <header className="bg-white border-b border-claude-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-claude-orange to-claude-orange-light rounded-xl flex items-center justify-center">
                <Shield className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-semibold text-claude-text">隐私政策合规审查</h1>
                <p className="text-xs text-claude-text-secondary">基于浙大CAPP-130 AI模型</p>
              </div>
            </div>
            <div className="flex items-center gap-2 text-xs text-claude-text-secondary">
              <Info className="w-4 h-4" />
              <span>RoBERTa/PERT • mT5</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Panel - Input */}
          <div className="space-y-4">
            <div className="bg-claude-card rounded-2xl shadow-card p-6 animate-fade-in">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <FileText className="w-5 h-5 text-claude-text-secondary" />
                  <h2 className="font-medium text-claude-text">输入隐私政策</h2>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={loadSample}
                    className="text-sm text-claude-blue hover:text-claude-blue-light transition-colors"
                  >
                    加载示例
                  </button>
                  <span className="text-claude-border">|</span>
                  <button
                    onClick={clearInput}
                    className="text-sm text-claude-text-secondary hover:text-risk-high transition-colors flex items-center gap-1"
                  >
                    <Trash2 className="w-4 h-4" />
                    清空
                  </button>
                </div>
              </div>
              
              <textarea
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder="粘贴隐私政策文本到这里...&#10;&#10;系统将自动识别其中的违规条款，并基于浙大CAPP-130的mT5模型生成整改建议。"
                className="w-full h-80 p-4 border border-claude-border rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-claude-blue/20 focus:border-claude-blue transition-all text-sm leading-relaxed"
              />
              
              <div className="flex items-center justify-between mt-4">
                <span className="text-sm text-claude-text-secondary">
                  {inputText.length} 字符
                </span>
                <button
                  onClick={handleAnalyze}
                  disabled={isAnalyzing || inputText.length < 10}
                  className={cn(
                    "px-6 py-2.5 bg-claude-orange hover:bg-claude-orange-dark text-white font-medium rounded-xl transition-all btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2",
                    isAnalyzing && "animate-pulse"
                  )}
                >
                  {isAnalyzing ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      分析中...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4" />
                      开始分析
                    </>
                  )}
                </button>
              </div>

              {error && (
                <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-risk-high">
                  {error}
                </div>
              )}
            </div>
          </div>

          {/* Right Panel - Output */}
          <div className="space-y-4">
            {result ? (
              <>
                {/* Score Card */}
                <div className="bg-claude-card rounded-2xl shadow-card p-6 animate-fade-in">
                  <div className="flex items-center gap-6">
                    {/* Progress Ring */}
                    <div className="relative w-28 h-28 flex-shrink-0">
                      <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
                        {/* Background circle */}
                        <circle
                          cx="50"
                          cy="50"
                          r="45"
                          fill="none"
                          stroke="#E5E7EB"
                          strokeWidth="8"
                        />
                        {/* Progress circle */}
                        <circle
                          cx="50"
                          cy="50"
                          r="45"
                          fill="none"
                          stroke={color}
                          strokeWidth="8"
                          strokeLinecap="round"
                          strokeDasharray={circumference}
                          strokeDashoffset={offset}
                          className="progress-ring"
                        />
                      </svg>
                      <div className="absolute inset-0 flex flex-col items-center justify-center">
                        <span className="text-3xl font-bold" style={{ color }}>{result.score}</span>
                        <span className="text-xs text-claude-text-secondary">合规评分</span>
                      </div>
                    </div>

                    {/* Info */}
                    <div className="flex-1 space-y-3">
                      <div>
                        <p className="text-sm text-claude-text-secondary">风险等级</p>
                        <div className="flex items-center gap-2 mt-1">
                          <span className={cn(
                            "px-3 py-1 rounded-full text-sm font-medium border",
                            getRiskLevelColor(result.risk_level)
                          )}>
                            {result.risk_level === 'high' ? '高风险' : result.risk_level === 'medium' ? '中风险' : '低风险'}
                          </span>
                        </div>
                      </div>
                      <div>
                        <p className="text-sm text-claude-text-secondary">检测结果</p>
                        <p className="text-sm font-medium mt-1">
                          <span className="text-risk-high">{result.violations.length}</span> 项违规 / 
                          <span className="text-risk-low"> {result.passed_indicators}</span> 项通过
                        </p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Violations List */}
                <div className="bg-claude-card rounded-2xl shadow-card p-6 animate-fade-in">
                  <div className="flex items-center gap-2 mb-4">
                    <AlertTriangle className="w-5 h-5 text-risk-high" />
                    <h3 className="font-medium text-claude-text">违规条款详情</h3>
                    <span className="text-xs text-claude-text-secondary ml-auto">
                      {result.violations.length} 项
                    </span>
                  </div>

                  <div className="space-y-3 max-h-96 overflow-y-auto pr-2">
                    {result.violations.map((violation, index) => (
                      <ViolationCard
                        key={violation.id}
                        violation={violation}
                        index={index + 1}
                        isExpanded={expandedViolations.has(violation.id)}
                        onToggle={() => toggleViolation(violation.id)}
                      />
                    ))}
                  </div>
                </div>
              </>
            ) : (
              <div className="bg-claude-card rounded-2xl shadow-card p-12 flex flex-col items-center justify-center text-center">
                <div className="w-16 h-16 bg-gray-100 rounded-2xl flex items-center justify-center mb-4">
                  <Shield className="w-8 h-8 text-claude-text-secondary" />
                </div>
                <h3 className="text-lg font-medium text-claude-text mb-2">
                  等待分析
                </h3>
                <p className="text-sm text-claude-text-secondary max-w-xs">
                  在左侧输入隐私政策文本，点击"开始分析"按钮，系统将使用浙大CAPP-130模型进行合规性检测。
                </p>
                <div className="mt-6 flex items-center gap-4 text-xs text-claude-text-secondary">
                  <div className="flex items-center gap-1">
                    <CheckCircle className="w-4 h-4 text-risk-low" />
                    <span>RoBERTa风险识别</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Sparkles className="w-4 h-4 text-claude-orange" />
                    <span>mT5整改建议</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Model Info Footer */}
        <div className="mt-8 p-4 bg-white rounded-xl border border-claude-border">
          <div className="flex items-center gap-2 mb-2">
            <Info className="w-4 h-4 text-claude-text-secondary" />
            <span className="text-sm font-medium text-claude-text">模型说明</span>
          </div>
          <p className="text-xs text-claude-text-secondary">
            本系统基于浙江大学 CAPP-130 数据集训练，使用 RoBERTa/PERT 模型进行风险条款识别（Risk-Micro F1 = 92.0%），
            使用微调后的 mT5 模型生成合规整改建议（ROUGE-L = 0.733）。<br/>
            论文链接：<a href="https://openreview.net/forum?id=OyTIV57Prb" target="_blank" className="text-claude-blue hover:underline">CAPP-130</a>，
            GitHub：<a href="https://github.com/EnlightenedAI/CAPP-130" target="_blank" className="text-claude-blue hover:underline">EnlightenedAI/CAPP-130</a>
          </p>
        </div>
      </main>
    </div>
  )
}

// Violation Card Component
function ViolationCard({ 
  violation, 
  index, 
  isExpanded, 
  onToggle 
}: { 
  violation: Violation
  index: number
  isExpanded: boolean
  onToggle: () => void
}) {
  return (
    <div className="border border-claude-border rounded-xl overflow-hidden violation-card">
      <button
        onClick={onToggle}
        className="w-full p-4 flex items-start gap-3 text-left hover:bg-gray-50 transition-colors"
      >
        <div className={cn(
          "w-6 h-6 rounded-lg flex items-center justify-center text-xs font-medium flex-shrink-0",
          violation.confidence >= 0.8 ? "bg-red-100 text-risk-high" :
          violation.confidence >= 0.6 ? "bg-yellow-100 text-risk-medium" :
          "bg-gray-100 text-claude-text-secondary"
        )}>
          {index}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-medium px-2 py-0.5 bg-gray-100 text-claude-text rounded">
              {violation.id}
            </span>
            <span className="text-sm font-medium text-claude-text truncate">
              {violation.type}
            </span>
            <span className="text-xs text-claude-text-secondary ml-auto">
              {formatConfidence(violation.confidence)}
            </span>
          </div>
          <p className="text-xs text-claude-text-secondary line-clamp-2">
            {violation.original_text}
          </p>
        </div>
        <div className="flex-shrink-0 text-claude-text-secondary">
          {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </div>
      </button>

      {isExpanded && (
        <div className="px-4 pb-4 pt-0 border-t border-claude-border bg-gray-50/50 animate-fade-in">
          <div className="pt-4 space-y-3">
            <div>
              <p className="text-xs font-medium text-claude-text-secondary mb-1">涉及法条</p>
              <p className="text-sm text-claude-text">{violation.law_article}</p>
            </div>
            <div>
              <p className="text-xs font-medium text-claude-text-secondary mb-1">违规原文</p>
              <p className="text-sm text-claude-text bg-white p-2 rounded border border-claude-border">
                {violation.original_text}
              </p>
            </div>
            <div>
              <div className="flex items-center gap-2 mb-1">
                <Sparkles className="w-3 h-3 text-claude-orange" />
                <p className="text-xs font-medium text-claude-text-secondary">整改建议 (mT5生成)</p>
              </div>
              <p className="text-sm text-claude-text leading-relaxed">
                {violation.suggestion}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
