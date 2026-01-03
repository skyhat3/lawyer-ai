#!/bin/bash
# 律师 AI 大模型应用安装脚本

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}   律师 AI 大模型应用安装脚本${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""

# 检查 Python 版本
echo -e "${YELLOW}检查 Python 版本...${NC}"
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

echo "检测到 Python 版本: $PYTHON_VERSION"

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 11 ]); then
    echo -e "${RED}错误: 需要 Python 3.11 或更高版本${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python 版本符合要求${NC}"
echo ""

# 检查 CUDA
echo -e "${YELLOW}检查 CUDA 环境...${NC}"
if command -v nvidia-smi &> /dev/null; then
    echo -e "${GREEN}✓ 检测到 GPU${NC}"
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
else
    echo -e "${YELLOW}⚠ 未检测到 GPU，将使用 CPU（性能较差）${NC}"
fi
echo ""

# 安装依赖
echo -e "${YELLOW}安装 Python 依赖包...${NC}"
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 依赖安装成功${NC}"
else
    echo -e "${RED}✗ 依赖安装失败${NC}"
    exit 1
fi
echo ""

# 检查模型路径
echo -e "${YELLOW}检查模型路径...${NC}"
MODEL_PATH="/workspace/llmexp/LLaMA-Factory/Qwen/Qwen2___5-7B-Instruct"
ADAPTER_PATH="/workspace/llmexp/saves/qwen2.5-7b_lawyer/lora/sft"

if [ -d "$MODEL_PATH" ]; then
    echo -e "${GREEN}✓ 基础模型路径存在: $MODEL_PATH${NC}"
else
    echo -e "${RED}✗ 基础模型路径不存在: $MODEL_PATH${NC}"
    echo "请确保模型已下载到正确路径"
fi

if [ -d "$ADAPTER_PATH" ]; then
    echo -e "${GREEN}✓ LoRA 权重路径存在: $ADAPTER_PATH${NC}"
else
    echo -e "${YELLOW}⚠ LoRA 权重路径不存在: $ADAPTER_PATH${NC}"
    echo "将使用基础模型进行推理"
fi
echo ""

# 创建环境变量文件
echo -e "${YELLOW}创建环境变量文件...${NC}"
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${GREEN}✓ 已创建 .env 文件（可编辑以自定义配置）${NC}"
else
    echo -e "${YELLOW}⚠ .env 文件已存在，跳过创建${NC}"
fi
echo ""

# 设置执行权限
echo -e "${YELLOW}设置脚本执行权限...${NC}"
chmod +x start.sh
echo -e "${GREEN}✓ 已设置执行权限${NC}"
echo ""

# 完成提示
echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}   安装完成！${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""
echo -e "${YELLOW}下一步：${NC}"
echo "1. 编辑 .env 文件以自定义配置（可选）"
echo "2. 运行测试：${GREEN}python test.py${NC}"
echo "3. 启动应用："
echo "   - Gradio 界面：${GREEN}./start.sh gradio${NC}"
echo "   - API 服务：${GREEN}./start.sh api${NC}"
echo "   - 同时启动：${GREEN}./start.sh both${NC}"
echo ""
echo -e "${YELLOW}快速开始：${NC}"
echo "查看 ${GREEN}QUICKSTART.md${NC} 获取快速启动指南"
echo ""
