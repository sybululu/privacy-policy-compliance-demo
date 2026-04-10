import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: '隐私政策合规审查 - 基于浙大CAPP-130',
  description: '使用浙大CAPP-130 AI模型进行隐私政策合规性分析，识别违规条款并生成整改建议',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh-CN">
      <body className="min-h-screen bg-claude-bg">
        {children}
      </body>
    </html>
  )
}
