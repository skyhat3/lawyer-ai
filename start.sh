#!/bin/bash
# 律师 AI 大模型应用启动脚本

# 设置环境变量
export CUDA_VISIBLE_DEVICES=0
export PYTHONPATH=/workspace/llmexp/LLaMA-Factory/src:$PYTHONPATH

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}   律师 AI 大模型应用启动脚本${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""

# 检查参数
if [ "$1" == "list" ]; then
    echo -e "${YELLOW}列出所有可用模型...${NC}"
    echo ""
    cd /workspace/llmexp
    python switch_model.py list

elif [ "$1" == "switch" ]; then
    if [ -z "$2" ]; then
        echo -e "${RED}错误：请指定模型 ID${NC}"
        echo ""
        echo "使用方法："
        echo "  ./start.sh switch <model_id>"
        echo ""
        echo "示例："
        echo "  ./start.sh switch qwen-1.5b"
        exit 1
    fi
    echo -e "${YELLOW}切换模型到: $2${NC}"
    echo ""
    cd /workspace/llmexp
    python switch_model.py switch $2
    echo ""
    echo -e "${YELLOW}请使用以下命令启动应用：${NC}"
    echo -e "  ${GREEN}./start.sh api${NC}     - 仅启动 FastAPI 服务器"
    echo -e "  ${GREEN}./start.sh gradio${NC}  - 仅启动 Gradio 界面"
    echo -e "  ${GREEN}./start.sh both${NC}    - 同时启动两者"

elif [ "$1" == "compare" ]; then
    if [ -z "$2" ] || [ -z "$3" ]; then
        echo -e "${RED}错误：请指定两个模型 ID${NC}"
        echo ""
        echo "使用方法："
        echo "  ./start.sh compare <model1> <model2>"
        echo ""
        echo "示例："
        echo "  ./start.sh compare qwen-7b qwen-1.5b"
        exit 1
    fi
    echo -e "${YELLOW}对比模型: $2 vs $3${NC}"
    echo ""
    cd /workspace/llmexp
    python switch_model.py compare $2 $3

elif [ "$1" == "api" ]; then
    echo -e "${YELLOW}启动 FastAPI 服务器...${NC}"
    echo -e "${GREEN}API 地址: http://localhost:8000${NC}"
    echo ""
    cd /workspace/llmexp
    python api_server.py

elif [ "$1" == "gradio" ]; then
    echo -e "${YELLOW}启动 Gradio 界面...${NC}"
    echo -e "${GREEN}访问地址: http://localhost:7860${NC}"
    echo ""
    cd /workspace/llmexp
    python app.py

elif [ "$1" == "both" ]; then
    echo -e "${YELLOW}同时启动 FastAPI 和 Gradio...${NC}"
    echo -e "${GREEN}Gradio: http://localhost:7860${NC}"
    echo -e "${GREEN}API: http://localhost:8000${NC}"
    echo ""

    # 启动 FastAPI（后台）
    cd /workspace/llmexp
    python api_server.py &
    API_PID=$!

    # 启动 Gradio（前台）
    python app.py

    # 清理
    kill $API_PID 2>/dev/null

else
    echo -e "${RED}错误：请指定启动模式${NC}"
    echo ""
    echo "使用方法："
    echo "  ${BLUE}模型管理：${NC}"
    echo "  ./start.sh list          - 列出所有可用模型"
    echo "  ./start.sh switch <id>   - 切换到指定模型"
    echo "  ./start.sh compare <m1> <m2> - 对比两个模型"
    echo ""
    echo "  ${BLUE}启动应用：${NC}"
    echo "  ./start.sh api           - 仅启动 FastAPI 服务器"
    echo "  ./start.sh gradio        - 仅启动 Gradio 界面"
    echo "  ./start.sh both           - 同时启动 FastAPI 和 Gradio"
    echo ""
    echo -e "${YELLOW}示例：${NC}"
    echo "  ./start.sh list                      # 查看所有模型"
    echo "  ./start.sh switch qwen-1.5b         # 切换到 1.5B 模型"
    echo "  ./start.sh compare qwen-7b qwen-1.5b # 对比两个模型"
    echo "  ./start.sh gradio                    # 启动 Gradio"
    exit 1
fi
