import gradio as gr
from analyzer import PrivacyPolicyAnalyzer
import os

# 初始化分析器
analyzer = PrivacyPolicyAnalyzer()

def analyze_privacy_policy(text):
    """分析隐私政策"""
    if len(text) < 50:
        return "请输入至少50个字符的隐私政策文本", None, []
    
    try:
        # 调用分析器
        result = analyzer.analyze(text)
        
        # 格式化输出
        output = f"""
## 合规评分: {result['score']}/100

**风险等级**: {result['risk_level']}

---
## 违规条款 ({len(result['violations'])}项)
"""
        
        for v in result['violations']:
            output += f"""
### {v['id']}: {v['title']}
- **严重程度**: {v['severity']}
- **问题描述**: {v['detail']}
- **法律依据**: {v['law']}
- **整改建议**: {v['suggestion']}
"""
        
        return output, result['score'], [(v['id'], v['severity']) for v in result['violations']]
    
    except Exception as e:
        return f"分析出错: {str(e)}", None, []

# 示例文本
sample_text = """隐私政策

更新日期：2024年1月1日

一、信息收集
我们收集您的个人信息包括：姓名、手机号码、电子邮箱、设备标识符、IP地址、位置信息等。我们会自动收集您的使用习惯和浏览记录。

二、信息使用
我们使用您的信息用于：提供和改进服务、发送营销信息、与第三方共享以提供更好的服务体验。

三、信息共享
我们可能与关联公司、业务合作伙伴、服务提供商共享您的个人信息。

四、信息安全
我们采取合理的安全措施保护您的信息。

五、用户权利
您可以在应用设置中查看和管理您的个人信息。如需删除账号，请联系客服。
"""

# 创建Gradio界面
with gr.Blocks(
    title="隐私政策合规审查",
    theme=gr.themes.Soft(
        primary_hue="orange",
        secondary_hue="yellow",
    )
) as demo:
    
    gr.Markdown("""
    # 🛡️ 隐私政策合规审查系统
    基于浙大CAPP-130 AI模型，智能识别隐私政策中的违规风险
    """)
    
    with gr.Row():
        with gr.Column(scale=1):
            input_text = gr.Textbox(
                label="隐私政策文本",
                placeholder="在此粘贴隐私政策文本...",
                lines=15,
                value=sample_text
            )
            analyze_btn = gr.Button("🔍 开始分析", variant="primary", size="lg")
            clear_btn = gr.Button("清空", variant="secondary")
        
        with gr.Column(scale=1):
            output_text = gr.Markdown(label="分析结果")
            score_slider = gr.Slider(
                minimum=0,
                maximum=100,
                label="合规评分",
                interactive=False
            )
    
    # 绑定事件
    analyze_btn.click(
        fn=analyze_privacy_policy,
        inputs=[input_text],
        outputs=[output_text, score_slider]
    )
    
    clear_btn.click(
        fn=lambda: ("", 50, []),
        outputs=[input_text, score_slider]
    )
    
    gr.Markdown("""
    ---
    ### 使用说明
    1. 粘贴隐私政策文本
    2. 点击"开始分析"
    3. 查看合规评分和违规条款
    
    ### 检测项目 (12项违规指示符)
    | 编号 | 违规类型 |
    |------|----------|
    | I1 | 收集范围超出必要 |
    | I2 | 未明确收集目的 |
    | I3 | 未获得用户同意 |
    | I4 | 收集敏感信息未单独告知 |
    | I5 | 共享第三方未告知 |
    | I6 | 共享第三方未获同意 |
    | I7 | 留存期限不合理 |
    | I8 | 未明确留存期限 |
    | I9 | 未提供删除途径 |
    | I10 | 未明确权利范围 |
    | I11 | 未提供便捷途径 |
    | I12 | 未明确响应时限 |
    
    ---
    **技术支持**: 浙江大学CAPP-130 | PERT模型 (F1=92.2%)
    """)

# 启动应用
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)