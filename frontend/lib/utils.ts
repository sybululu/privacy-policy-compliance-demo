// 工具函数

import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// 计算进度环的周长和偏移量
export function getProgressRingProps(score: number) {
  const radius = 45
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (score / 100) * circumference
  
  // 颜色渐变：红 -> 黄 -> 绿
  let color = '#22C55E' // green
  if (score < 40) {
    color = '#EF4444' // red
  } else if (score < 70) {
    color = '#F59E0B' // yellow
  }
  
  return {
    circumference,
    offset,
    color
  }
}

// 风险等级颜色
export function getRiskLevelColor(level: string) {
  switch (level) {
    case 'high':
      return 'text-risk-high bg-red-50 border-red-200'
    case 'medium':
      return 'text-risk-medium bg-yellow-50 border-yellow-200'
    case 'low':
      return 'text-risk-low bg-green-50 border-green-200'
    default:
      return 'text-gray-500 bg-gray-50 border-gray-200'
  }
}

// 格式化置信度
export function formatConfidence(confidence: number) {
  return `${(confidence * 100).toFixed(1)}%`
}
