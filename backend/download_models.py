"""
下载浙大CAPP-130预训练模型
"""
import os
import logging
import sys

try:
    from huggingface_hub import snapshot_download
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False
    print("huggingface_hub not available, will use direct model loading")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 浙大TCSI_pp_zh模型仓库
MODEL_REPO = "EnlightenedAI/TCSI_pp_zh"

def download_models():
    """下载所有预训练模型"""
    if not HF_AVAILABLE:
        logger.warning("huggingface_hub not installed, skipping download")
        return
        
    try:
        logger.info(f"正在从HuggingFace下载模型: {MODEL_REPO}")
        
        # 下载整个仓库
        local_dir = snapshot_download(
            repo_id=MODEL_REPO,
            local_dir="./models/tcsi_pp_zh",
            local_dir_use_symlinks=False
        )
        
        logger.info(f"模型下载完成，保存到: {local_dir}")
        
        # 列出下载的文件
        for root, dirs, files in os.walk("./models/tcsi_pp_zh"):
            for f in files:
                filepath = os.path.join(root, f)
                size = os.path.getsize(filepath) / (1024*1024)  # MB
                logger.info(f"  {filepath}: {size:.2f} MB")
                
    except Exception as e:
        logger.error(f"下载失败: {e}")
        logger.info("将使用备用方案：直接从HuggingFace加载模型")

if __name__ == "__main__":
    download_models()
