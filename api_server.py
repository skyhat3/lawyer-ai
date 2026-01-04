#!/usr/bin/env python3
"""
律师 AI 大模型 FastAPI 服务器
提供 RESTful API 接口
"""

import os
import re
import yaml
from typing import List, Optional
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

# 设置环境变量
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

from llamafactory.chat import ChatModel


# 配置文件路径
CONFIG_FILE = Path(__file__).parent / "config_models.yaml"


def load_model_config():
    """从配置文件加载模型配置"""
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            current_id = config.get('current_model', 'qwen-7b')
            models = config.get('models', {})
            if current_id in models:
                return models[current_id]
            else:
                print(f"⚠️  警告: 模型 '{current_id}' 不存在，使用默认配置")
                return {}
    except Exception as e:
        print(f"⚠️  警告: 无法加载配置文件，使用默认配置: {e}")
        return {}


# 请求和响应模型
class Message(BaseModel):
    role: str = Field(..., description="消息角色：user, assistant, system")
    content: str = Field(..., description="消息内容")


class ChatRequest(BaseModel):
    messages: List[Message] = Field(..., description="对话历史消息列表")
    temperature: float = Field(0.8, ge=0.1, le=2.0, description="温度参数")
    max_tokens: int = Field(512, ge=64, le=1024, description="最大生成长度")
    top_p: float = Field(0.9, ge=0.1, le=1.0, description="Top-p 采样参数")
    stream: bool = Field(False, description="是否使用流式输出")
    enable_law_links: bool = Field(True, description="是否启用法规超链接")


class ChatResponse(BaseModel):
    role: str = Field(default="assistant", description="回复角色")
    content: str = Field(..., description="回复内容")
    law_references: List[dict] = Field(default_factory=list, description="法规引用列表")


class LawReference(BaseModel):
    text: str = Field(..., description="法规文本")
    link: str = Field(..., description="搜索链接")


# 全局变量
chat_model: Optional[ChatModel] = None


# 法规关键词提取配置
LAW_PATTERNS = [
    r'第[一二三四五六七八九十百千万零]+条',
    r'第[0-9]+条',
    r'第[一二三四五六七八九十百千万零]+款',
    r'第[0-9]+款',
    r'第[一二三四五六七八九十百千万零]+项',
    r'第[0-9]+项',
    r'《[^》]+法》',
    r'《[^》]+条例》',
    r'《[^》]+规定》',
    r'《[^》]+办法》',
    r'《[^》]+细则》',
    r'《[^》]+解释》',
    r'《[^》]+编》',  # 新增行，用于匹配以“编》”结尾的法规名称
]


def extract_law_references(text: str) -> List[LawReference]:
    """提取文本中的法规引用"""
    law_refs = []
    seen = set()  # 避免重复

    for pattern in LAW_PATTERNS:
        matches = re.finditer(pattern, text)
        for match in matches:
            law_text = match.group()
            if law_text not in seen:
                seen.add(law_text)
                search_url = f"https://www.baidu.com/s?wd={law_text}"
                law_refs.append(LawReference(text=law_text, link=search_url))

    return law_refs


def add_law_links(text: str) -> str:
    """为法规引用添加超链接"""
    result = text
    seen = set()

    for pattern in LAW_PATTERNS:
        def replace_with_link(match):
            law_text = match.group()
            if law_text in seen:
                return law_text  # 避免重复替换
            seen.add(law_text)
            search_url = f"https://www.baidu.com/s?wd={law_text}"
            return f'[{law_text}](https://www.baidu.com/s?wd={law_text})'

        result = re.sub(pattern, replace_with_link, result)

    return result


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global chat_model

    # 启动时加载模型
    print("正在加载模型...")
    try:
        # 从配置文件加载模型配置
        model_config = load_model_config()

        if model_config:
            print(f"使用模型: {model_config['name']}")
            args = {
                "model_name_or_path": model_config['model_name_or_path'],
                "adapter_name_or_path": model_config['adapter_name_or_path'],
                "template": model_config['template'],
                "finetuning_type": model_config['finetuning_type'],
            }
            print(f"  - 基础模型: {model_config['model_name_or_path']}")
            print(f"  - LoRA 权重: {model_config['adapter_name_or_path']}")
        else:
            print("使用默认配置...")
            args = {
                "model_name_or_path": "/workspace/llmexp/LLaMA-Factory/Qwen/Qwen2___5-7B-Instruct",
                "adapter_name_or_path": "/workspace/llmexp/saves/qwen2.5-7b_lawyer/lora/sft",
                "template": "Qwen",
                "finetuning_type": "lora",
            }

        chat_model = ChatModel(args=args)
        print("模型加载完成！")
    except Exception as e:
        print(f"模型加载失败: {e}")
        raise

    yield

    # 关闭时清理资源
    print("正在清理资源...")
    del chat_model
    print("资源清理完成！")


# 创建 FastAPI 应用
app = FastAPI(
    title="律师 AI 助手 API",
    description="基于 LLaMA-Factory 微调的 Qwen2.5-7B 法律大模型 API",
    version="1.0.0",
    lifespan=lifespan,
)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["主页"])
async def root():
    """根路径 - 返回测试页面"""
    return FileResponse(Path(__file__).parent / "test_api.html")


@app.get("/api", tags=["API 信息"])
async def api_info():
    """API 信息"""
    return {
        "message": "律师 AI 助手 API 服务运行中",
        "status": "ok",
        "version": "1.0.0"
    }


@app.get("/health", tags=["健康检查"])
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "model_loaded": chat_model is not None
    }


@app.post("/v1/chat/completions", response_model=ChatResponse, tags=["对话"])
async def chat_completion(request: ChatRequest):
    """
    对话补全接口

    - 支持多轮对话
    - 自动为法规引用添加超链接
    - 支持流式输出（需要客户端支持 SSE）
    """
    if chat_model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="模型未加载完成"
        )

    try:
        # 转换消息格式
        formatted_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in request.messages
        ]

        # 调用模型生成回复
        response = chat_model.chat(
            formatted_messages,
            max_new_tokens=request.max_tokens,
            temperature=request.temperature,
            top_p=request.top_p,
        )

        # 提取回复文本
        response_text = response[0].response_text

        # 如果启用了法规超链接
        if request.enable_law_links:
            response_text = add_law_links(response_text)

        # 提取法规引用
        law_refs = extract_law_references(response[0].response_text)

        return ChatResponse(
            role="assistant",
            content=response_text,
            law_references=[{"text": ref.text, "link": ref.link} for ref in law_refs]
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"处理请求时出错：{str(e)}"
        )


@app.post("/v1/chat/analyze", tags=["分析"])
async def analyze_law_references(messages: List[Message]):
    """
    分析对话中的法规引用

    返回对话中所有识别到的法规条文及其搜索链接
    """
    all_law_refs = []
    seen = set()

    for msg in messages:
        law_refs = extract_law_references(msg.content)
        for ref in law_refs:
            if ref.text not in seen:
                seen.add(ref.text)
                all_law_refs.append({"text": ref.text, "link": ref.link})

    return {
        "count": len(all_law_refs),
        "law_references": all_law_refs
    }


@app.get("/v1/models", tags=["模型信息"])
async def list_models():
    """列出可用模型"""
    return {
        "object": "list",
        "data": [
            {
                "id": "qwen2.5-7b-lawyer",
                "object": "model",
                "owned_by": "lawyer-ai",
                "permission": [],
                "root": "qwen2.5-7b-lawyer",
                "parent": None
            }
        ]
    }


@app.get("/v1/model/info", tags=["模型信息"])
async def model_info():
    """获取模型详细信息"""
    return {
        "model_name": "Qwen2.5-7B-Lawyer",
        "base_model": "Qwen2.5-7B-Instruct",
        "finetuning_type": "LoRA",
        "description": "基于 LLaMA-Factory 微调的法律大模型，专门用于法律咨询和案例分析",
        "capabilities": [
            "法律咨询",
            "法规条文解释",
            "案例分析",
            "合同审查"
        ],
        "features": {
            "law_link_detection": True,
            "stream_output": True,
            "multi_turn_dialogue": True
        }
    }


if __name__ == "__main__":
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
