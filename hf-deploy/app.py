"""
隐私政策合规审查 - HF Space
从 sybululu/bert-moe 仓库动态加载模型
支持A/B版本切换
"""
import gradio as gr
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, MT5ForConditionalGeneration
from huggingface_hub import hf_hub_download
import logging
import os

# 导入版本配置和规则映射
from config import VERSION, get_config, get_version_info
from mapper import map_to_violations, format_violation_result, CAPP130_LABELS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 全局模型
models = {}

def load_models():
    """从HF Hub加载模型"""
    if models:
        return
    
    # 获取当前版本配置
    config = get_config()
    logger.info(f"加载模型，版本: {get_version_info()}")
    
    # 1. 分类模型 - 从 bert-moe 仓库加载
    try:
        logger.info("加载分类模型...")
        
        # 使用动态配置加载基础模型架构
        models["tokenizer_cls"] = AutoTokenizer.from_pretrained(config["base_model"])
        models["model_cls"] = AutoModelForSequenceClassification.from_pretrained(
            config["base_model"],
            num_labels=config["num_labels"]
        )
        
        # 从 bert-moe 仓库下载 checkpoint
        ckpt_path = hf_hub_download(
            repo_id="sybululu/bert-moe",
            filename="multi_classification_bertmoe.ckpt",
            repo_type="model"
        )
        logger.info(f"Checkpoint 下载到: {ckpt_path}")
        
        # 加载 checkpoint 并提取权重
        checkpoint = torch.load(ckpt_path, map_location="cpu")
        
        # 常见的checkpoint格式处理
        if "state_dict" in checkpoint:
            state_dict = checkpoint["state_dict"]
        elif "model_state_dict" in checkpoint:
            state_dict = checkpoint["model_state_dict"]
        else:
            state_dict = checkpoint
        
        # 过滤掉不匹配的key（如果有前缀）
        new_state_dict = {}
        for k, v in state_dict.items():
            # 移除可能的前缀
            if k.startswith("model."):
                k = k[6:]
            new_state_dict[k] = v
        
        # 加载权重
        models["model_cls"].load_state_dict(new_state_dict, strict=False)
        models["model_cls"].eval()
        
        logger.info("✅ 分类模型加载成功（已加载微调权重）")
    except Exception as e:
        logger.error(f"❌ 分类模型加载失败: {e}")
        logger.info("⚠️ 将使用基础模型（未微调）")
    
    # 2. 生成模型 - 从 bert-moe 仓库加载 mT5
    try:
        logger.info("加载生成模型...")
        
        # 加载基础模型架构
        models["tokenizer_gen"] = AutoTokenizer.from_pretrained("google/mt5-small")
        models["model_gen"] = MT5ForConditionalGeneration.from_pretrained("google/mt5-small")
        
        # 从 bert-moe 仓库下载 mT5 checkpoint
        try:
            ckpt_path = hf_hub_download(
                repo_id="sybululu/bert-moe",
                filename="rewrite_mT5_small.ckpt",
                repo_type="model"
            )
            logger.info(f"mT5 Checkpoint 下载到: {ckpt_path}")
            
            checkpoint = torch.load(ckpt_path, map_location="cpu")
            
            if "state_dict" in checkpoint:
                state_dict = checkpoint["state_dict"]
            elif "model_state_dict" in checkpoint:
                state_dict = checkpoint["model_state_dict"]
            else:
                state_dict = checkpoint
            
            # 处理 key 前缀
            new_state_dict = {}
            for k, v in state_dict.items():
                if k.startswith("model."):
                    k = k[6:]
                new_state_dict[k] = v
            
            models["model_gen"].load_state_dict(new_state_dict, strict=False)
            models["model_gen"].eval()
            
            logger.info("✅ 生成模型加载成功（已加载微调权重）")
        except Exception as e:
            logger.warning(f"⚠️ mT5 checkpoint 加载失败: {e}")
            logger.info("⚠️ 将使用基础 mT5 模型")
            
    except Exception as e:
        logger.error(f"❌ 生成模型加载失败: {e}")
    
    logger.info("模型加载完成")

def analyze(text):
    """分析隐私政策"""
    if not models:
        return "模型未加载"
    
    if not models.get("model_cls"):
        return "分类模型未加载"
    
    config = get_config()
    
    try:
        # 分类推理
        inputs = models["tokenizer_cls"](text, return_tensors="pt", truncation=True, max_length=512)
        outputs = models["model_cls"](**inputs)
        probs = outputs.logits.softmax(dim=-1)
        pred_label = probs.argmax().item()
        
        if VERSION == "A":
            # A版：11类 → 12类违规映射
            violations = map_to_violations(probs)
            result = format_violation_result(violations)
            
            # 附加原始分类信息
            result += f"\n\n**原始分类**: {CAPP130_LABELS[pred_label]} ({probs[0][pred_label]:.1%})"
            
        else:
            # B版：直接输出12类违规
            # 使用 config 中的 num_labels 确保正确切片
            num_labels = config["num_labels"]
            probs_12 = probs[0][:num_labels]
            pred_label = probs_12.argmax().item()
            
            # 构建违规字典（使用 I1, I2 格式的 key）
            violations = {}
            for i in range(num_labels):
                key = f"I{i+1}"
                violations[key] = probs_12[i].item()
            
            # 使用统一的格式化函数
            result = format_violation_result(violations)
            result += f"\n\n**预测类型**: {config['labels'][pred_label]} ({probs_12[pred_label]:.1%})"
        
        return result
    except Exception as e:
        return f"分析失败: {e}"

# Gradio界面
with gr.Blocks(title="隐私政策合规审查") as demo:
    gr.Markdown("# 隐私政策合规审查")
    gr.Markdown(f"**{get_version_info()}**")
    
    with gr.Row():
        load_btn = gr.Button("加载模型", variant="primary")
        status = gr.Textbox(label="状态", value="未加载", interactive=False)
    
    with gr.Row():
        text_input = gr.Textbox(
            label="输入隐私政策文本", 
            lines=10, 
            placeholder="粘贴隐私政策文本进行分析..."
        )
        output = gr.Textbox(label="分析结果", lines=15, interactive=False)
    
    analyze_btn = gr.Button("开始分析", variant="secondary")
    
    def load_and_status():
        load_models()
        status_parts = []
        if models.get("model_cls"):
            status_parts.append("✅ 分类模型")
        else:
            status_parts.append("❌ 分类模型")
        
        if models.get("model_gen"):
            status_parts.append("✅ 生成模型")
        else:
            status_parts.append("❌ 生成模型")
        
        return " | ".join(status_parts)
    
    load_btn.click(load_and_status, outputs=status)
    analyze_btn.click(analyze, inputs=text_input, outputs=output)

# 启动时自动加载模型
load_models()

# 启动Gradio应用
if __name__ == "__main__":
    demo.launch()

# HF Space需要app变量
app = demo
