# 部署指南

## 准备工作

在部署本项目之前，您需要准备以下资源：

### 1. LLaMA-Factory 框架

```bash
git clone https://github.com/hiyouga/LLaMA-Factory.git
cd LLaMA-Factory
pip install -e .
```

### 2. 基座模型

下载通义千问基座模型：

**Qwen2.5-7B**:
```bash
# 使用 huggingface-cli
pip install huggingface_hub
huggingface-cli download Qwen/Qwen2.5-7B-Instruct --local-dir /path/to/Qwen2.5-7B-Instruct
```

**Qwen2.5-1.5B**:
```bash
huggingface-cli download Qwen/Qwen2.5-1.5B-Instruct --local-dir /path/to/Qwen2.5-1.5B-Instruct
```

### 3. LoRA 微调权重

如果您有自己的微调权重，请将它们放置在 `saves/` 目录下。目录结构应如下：

```
saves/
├── qwen2.5-7b_lawyer/
│   └── lora/
│       └── sft/
│           ├── adapter_config.json
│           ├── adapter_model.safetensors
│           └── ...
└── qwen2.5-1.5b_lawyer/
    └── lora/
        └── sft/
            ├── adapter_config.json
            └── ...
```

## 配置文件

### 1. 复制环境变量配置

```bash
cp .env.example .env
```

### 2. 编辑 .env 文件

根据您的实际路径修改以下配置：

```env
# 模型路径（修改为您的实际路径）
MODEL_NAME_OR_PATH=/path/to/LLaMA-Factory/Qwen/Qwen2___5-7B-Instruct
ADAPTER_NAME_OR_PATH=/path/to/saves/qwen2.5-7b_lawyer/lora/sft

# GPU 配置
CUDA_VISIBLE_DEVICES=0

# 端口配置
API_PORT=8000
GRADIO_PORT=7860
```

### 3. 编辑 config_models.yaml

更新模型路径：

```yaml
models:
  qwen-7b:
    model_name_or_path: /path/to/LLaMA-Factory/Qwen/Qwen2___5-7B-Instruct
    adapter_name_or_path: /path/to/saves/qwen2.5-7b_lawyer/lora/sft
    template: Qwen
    finetuning_type: lora

  qwen-1.5b:
    model_name_or_path: /path/to/LLaMA-Factory/Qwen/Qwen2.5-1.5B-Instruct
    adapter_name_or_path: /path/to/saves/qwen2.5-1.5b_lawyer/lora/sft
    template: Qwen
    finetuning_type: lora
```

## 安装依赖

```bash
pip install -r requirements.txt
```

或者使用提供的安装脚本：

```bash
chmod +x install.sh
./install.sh
```

## 启动服务

### 使用一键启动脚本

```bash
chmod +x start.sh
./start.sh gradio    # 启动 Gradio 界面
./start.sh api       # 启动 FastAPI 服务
./start.sh both      # 同时启动两个服务
```

### 手动启动

**Gradio 界面**:
```bash
python app.py
```

**FastAPI 服务**:
```bash
python api_server.py
```

## 访问应用

- **Gradio 界面**: http://localhost:7860
- **FastAPI**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs

## 模型切换

查看所有模型：
```bash
./start.sh list
```

切换模型：
```bash
./start.sh switch qwen-7b    # 切换到 7B 模型
./start.sh switch qwen-1.5b  # 切换到 1.5B 模型
```

对比模型：
```bash
./start.sh compare qwen-7b qwen-1.5b
```

## Docker 部署（可选）

### 1. 构建 Docker 镜像

```bash
docker build -t lawyer-ai:latest .
```

### 2. 运行容器

```bash
docker run -d \
  --gpus all \
  -p 8000:8000 \
  -p 7860:7860 \
  -v /path/to/models:/workspace/models \
  -v /path/to/saves:/workspace/saves \
  -e CUDA_VISIBLE_DEVICES=0 \
  --name lawyer-ai \
  lawyer-ai:latest
```

## 常见问题

### Q1: 模型加载失败

**A**: 检查以下几点：
1. 模型路径是否正确
2. LoRA 权重是否存在
3. GPU 显存是否足够（7B 模型需要约 14GB）
4. CUDA 是否正确安装

### Q2: 端口被占用

**A**: 修改 `.env` 文件中的端口配置：
```env
API_PORT=8001
GRADIO_PORT=7861
```

### Q3: 依赖安装失败

**A**: 尝试使用国内镜像源：
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 性能优化建议

1. **使用模型量化**（可选）：
   ```bash
   # 使用 vllm 加速推理（需要额外安装）
   pip install vllm
   ```

2. **增加批处理大小**：
   编辑配置文件，根据显存大小调整 `per_device_train_batch_size`

3. **使用多 GPU**：
   ```bash
   CUDA_VISIBLE_DEVICES=0,1,2,3 python app.py
   ```

## 技术支持

如有问题，请查看 [README.md](README.md) 或提交 Issue。
