# 律师 AI 大模型应用

基于 LLaMA-Factory 微调的律师 AI 大模型，支持 Gradio/FastAPI 部署，自动识别法规条文并生成搜索链接。

## 📋 目录

- [快速开始](#快速开始)
- [模型切换](#模型切换)
- [功能特性](#功能特性)
- [API 使用](#api-使用)
- [常见问题](#常见问题)

---

## 🚀 快速开始

### 1. 安装依赖

```bash
cd /workspace/llmexp
pip install -r requirements.txt
```
### 2. 启动应用
部署请参考(#DEPLOYMENT.md)
### 3. 启动应用

```bash
# 方式一：Gradio 界面（推荐）
./start.sh gradio

# 方式二：FastAPI 服务
./start.sh api

# 方式三：同时启动
./start.sh both
```

### 4. 访问应用

- **Gradio 界面**: http://localhost:7860
- **FastAPI**: http://localhost:8000
- **Web 测试页**: http://localhost:8000 （自动加载）

---

## 🔄 模型切换

支持多个模型之间快速切换和对比。

### 查看所有模型

```bash
./start.sh list
```

### 切换模型

```bash
# 切换到 1.5B 模型
./start.sh switch qwen-1.5b

# 切换到 7B 模型
./start.sh switch qwen-7b
```

### 对比模型

```bash
./start.sh compare qwen-7b qwen-1.5b
```

### 添加新模型

编辑 `config_models.yaml`：

```yaml
models:
  qwen-7b:
    name: "Qwen2.5-7B-Lawyer"
    model_name_or_path: "/path/to/base/model"
    adapter_name_or_path: "/path/to/lora/weights"
    template: "Qwen"
    finetuning_type: "lora"

  your-new-model:
    name: "Your Model Name"
    model_name_or_path: "/path/to/base/model"
    adapter_name_or_path: "/path/to/lora/weights"
    template: "Qwen"
    finetuning_type: "lora"

current_model: "qwen-7b"
```

---

## ✨ 功能特性

### 1. 法规超链接自动生成

模型输出中的法规条文会自动转换为搜索链接：

```
根据《刑法》第二十条的规定...
```

转换为：

```
根据[《刑法》](https://www.baidu.com/s?wd=《刑法》)[第二十条](https://www.baidu.com/s?wd=第二十条)的规定...
```

点击链接可直接在搜索引擎中验证法规。

### 2. Gradio 界面

- 友好的 Web 界面，无需编程
- 实时参数调节（温度、最大长度等）
- 多轮对话支持
- 示例问题展示

### 3. FastAPI 服务

- 标准的 RESTful API
- OpenAPI 文档自动生成
- 支持流式输出
- 健康检查接口

---

## 📡 API 使用

### 对话接口

```bash
curl -X POST "http://localhost:8000/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "什么是正当防卫？"}
    ],
    "temperature": 0.7,
    "max_tokens": 2048
  }'
```

### Python 客户端

```python
import requests

response = requests.post(
    "http://localhost:8000/v1/chat/completions",
    json={
        "messages": [
            {"role": "user", "content": "什么是正当防卫？"}
        ]
    }
)

print(response.json()["response"])
```

### API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/` | GET | Web 测试页面 |
| `/health` | GET | 健康检查 |
| `/v1/chat/completions` | POST | 对话接口 |
| `/v1/model/info` | GET | 模型信息 |

---

## ❓ 常见问题

### Q1: 切换模型后需要重启吗？

**A:** 是的，切换模型后必须重启应用：

```bash
./start.sh switch qwen-1.5b  # 切换配置
./start.sh gradio             # 重启应用
```

### Q2: 模型加载需要多久？

**A:**
- 7B 模型: 约 3-5 分钟
- 1.5B 模型: 约 1-2 分钟

### Q3: 如何查看当前使用的模型？

**A:**
```bash
./start.sh list
```

当前模型会标记为 `[当前]`。

### Q4: API 返回的是什么格式？

**A:** 标准的 JSON 格式：

```json
{
  "response": "AI 回复内容（包含法规链接）",
  "model": "当前模型名称",
  "latency": 1.23
}
```

### Q5: 法规链接失效怎么办？

**A:** 链接指向百度搜索，如果失效可以：
1. 手动复制法条名搜索
2. 修改 `add_law_links()` 函数中的搜索引擎 URL

### Q6: 支持哪些法规格式？

**A:** 支持以下格式：
- 《XXX法》
- 第X条
- 第X款
- XX法第X条
- 等等

---

## 📚 项目结构

```
llmexp/
├── app.py                 # Gradio 界面
├── api_server.py          # FastAPI 服务
├── config_models.yaml     # 模型配置文件
├── switch_model.py        # 模型切换工具
├── start.sh               # 启动脚本
├── test_api.html          # Web 测试页面
├── requirements.txt       # 依赖列表
└── README.md              # 本文档
```

---

## 🛠️ 高级用法

### 修改法规链接搜索引擎

编辑 `api_server.py` 和 `app.py` 中的 `add_law_links()` 函数：

```python
# 使用百度
url = f"https://www.baidu.com/s?wd={quote(law)}"

# 使用 Google
url = f"https://www.google.com/search?q={quote(law)}"

# 使用必应
url = f"https://www.bing.com/search?q={quote(law)}"
```

### 自定义法规识别规则

编辑 `add_law_links()` 函数中的正则表达式：

```python
# 添加新的识别规则
patterns = [
    r'《([^》]+)》',           # 法规名称
    r'第(\d+)条',            # 法条号
    r'第(\d+)款',            # 款号
    # 添加你的规则...
]
```

---

## 📞 技术支持

- **LLaMA-Factory**: /workspace/llmexp/LLaMA-Factory
- **文档**: 本 README.md

---

## 📄 许可证

本项目基于 LLaMA-Factory 开发。
