# 快速开始

## 5 分钟快速上手

### 前置要求

- Python 3.8+
- CUDA 11.8+ (GPU 推荐)
- 至少 12GB 显存（7B 模型）

### 步骤 1: 克隆仓库

```bash
git clone https://github.com/your-username/lawyer-ai.git
cd lawyer-ai
```

### 步骤 2: 安装 LLaMA-Factory

```bash
git clone https://github.com/hiyouga/LLaMA-Factory.git
cd LLaMA-Factory
pip install -e .
cd ..
```

### 步骤 3: 下载模型

```bash
# 安装 huggingface-hub
pip install huggingface-hub

# 下载 7B 模型（约 14GB）
huggingface-cli download Qwen/Qwen2.5-7B-Instruct --local-dir ./Qwen2.5-7B-Instruct

# 或下载 1.5B 模型（约 3GB）
huggingface-cli download Qwen/Qwen2.5-1.5B-Instruct --local-dir ./Qwen2.5-1.5B-Instruct
```

### 步骤 4: 配置环境

```bash
# 复制配置文件
cp .env.example .env

# 编辑 .env 文件，修改模型路径
nano .env
```

在 `.env` 文件中修改：
```env
MODEL_NAME_OR_PATH=./Qwen2.5-7B-Instruct
```

### 步骤 5: 安装依赖

```bash
pip install -r requirements.txt
```

### 步骤 6: 启动应用

```bash
# 给脚本添加执行权限
chmod +x start.sh install.sh

# 启动 Gradio 界面
./start.sh gradio
```

### 步骤 7: 访问应用

打开浏览器访问：http://localhost:7860

---

## 常用命令

### 启动应用

```bash
./start.sh gradio    # Gradio 界面
./start.sh api       # FastAPI 服务
./start.sh both      # 同时启动
```

### 模型管理

```bash
./start.sh list           # 查看所有模型
./start.sh switch <model> # 切换模型
./start.sh compare <m1> <m2> # 对比模型
```

### API 测试

```bash
# 使用测试脚本
python client_example.py

# 或使用 Web 测试页面
# 访问 http://localhost:8000
```

---

## 示例问题

启动 Gradio 界面后，可以尝试以下问题：

1. "什么是正当防卫？"
2. "合同违约需要承担什么责任？"
3. "劳动法规定的工作时间是多少？"
4. "请解释刑法中故意犯罪的概念"

---

## 下一步

- 阅读 [README.md](README.md) 了解更多功能
- 查看 [DEPLOYMENT.md](DEPLOYMENT.md) 了解详细部署指南

---

## 获取帮助

- 📖 查看文档：[README.md](README.md)
- 🐛 提交问题：GitHub Issues
- 💬 讨论交流：GitHub Discussions
