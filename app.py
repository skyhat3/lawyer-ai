#!/usr/bin/env python3
"""
律师 AI 大模型前端应用
基于 Gradio 和 FastAPI 的部署方案
"""

import os
import re
import yaml
import gradio as gr
from typing import List, Tuple
from pathlib import Path

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


# 法规关键词提取和超链接生成配置
LAW_PATTERNS = [
    # 法条格式：第X条、第X款等
    r'第[一二三四五六七八九十百千万零]+条',
    r'第[0-9]+条',
    r'第[一二三四五六七八九十百千万零]+款',
    r'第[0-9]+款',
    r'第[一二三四五六七八九十百千万零]+项',
    r'第[0-9]+项',
    # 常见法律法规名称
    r'《[^》]+法》',
    r'《[^》]+条例》',
    r'《[^》]+规定》',
    r'《[^》]+办法》',
    r'《[^》]+细则》',
    r'《[^》]+解释》',
]


class LawyerChatApp:
    def __init__(self):
        """初始化律师 AI 聊天应用"""
        print("正在加载模型...")

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

        self.chat_model = ChatModel(args=args)
        self.chat_history = []
        print("模型加载完成！")

    def extract_law_references(self, text: str) -> List[Tuple[str, str]]:
        """提取文本中的法规引用"""
        law_refs = []
        for pattern in LAW_PATTERNS:
            matches = re.finditer(pattern, text)
            for match in matches:
                law_text = match.group()
                # 生成搜索引擎链接（使用百度）
                search_url = f"https://www.baidu.com/s?wd={law_text}"
                law_refs.append((law_text, search_url))
        return law_refs

    def add_law_links(self, text: str) -> str:
        """为法规引用添加超链接"""
        result = text
        # 使用 HTML 标记添加超链接
        for pattern in LAW_PATTERNS:
            def replace_with_link(match):
                law_text = match.group()
                search_url = f"https://www.baidu.com/s?wd={law_text}"
                return f'<a href="{search_url}" target="_blank" style="color: #1E88E5; text-decoration: underline;">{law_text}</a>'
            result = re.sub(pattern, replace_with_link, result)
        return result

    def format_history_for_model(self, history: List[Tuple[str, str]]) -> List[dict]:
        """将聊天历史转换为模型需要的格式"""
        messages = []
        for user_msg, assistant_msg in history:
            messages.append({"role": "user", "content": user_msg})
            if assistant_msg:
                messages.append({"role": "assistant", "content": assistant_msg})
        return messages

    def chat(self, message: str, history: List[Tuple[str, str]]) -> Tuple[str, List[Tuple[str, str]]]:
        """
        处理用户输入并生成回复

        Args:
            message: 用户输入的消息
            history: 聊天历史记录

        Returns:
            Tuple[assistant_message, updated_history]
        """
        try:
            # 格式化历史记录
            formatted_history = self.format_history_for_model(history)
            formatted_history.append({"role": "user", "content": message})

            # 调用模型生成回复
            response = self.chat_model.chat(
                formatted_history,
                max_new_tokens=512,
                temperature=0.8,
                top_p=0.9,
            )

            # 提取回复文本（注意：response 是一个列表）
            response_text = response[0].response_text

            # 为法规引用添加超链接
            assistant_message_with_links = self.add_law_links(response_text)

            # 更新历史记录
            history.append((message, assistant_message_with_links))

            return assistant_message_with_links, history

        except Exception as e:
            error_msg = f"抱歉，处理过程中出现错误：{str(e)}"
            return error_msg, history

    def stream_chat(self, message: str, history: List[Tuple[str, str]]):
        """
        流式聊天生成

        Args:
            message: 用户输入的消息
            history: 聊天历史记录

        Yields:
            生成的文本片段
        """
        try:
            # 格式化历史记录
            formatted_history = self.format_history_for_model(history)
            formatted_history.append({"role": "user", "content": message})

            # 流式生成
            full_response = ""
            for new_token in self.chat_model.stream_chat(
                formatted_history,
                max_new_tokens=512,
                temperature=0.8,
                top_p=0.9,
            ):
                full_response += new_token
                yield full_response

            # 为法规引用添加超链接
            full_response_with_links = self.add_law_links(full_response)
            yield full_response_with_links

        except Exception as e:
            yield f"抱歉，处理过程中出现错误：{str(e)}"

    def clear_history(self):
        """清除聊天历史"""
        return [], []


def create_interface():
    """创建 Gradio 界面"""
    # 初始化应用
    app = LawyerChatApp()

    # 自定义 CSS
    custom_css = """
    .chat-message {
        padding: 12px 16px;
        border-radius: 12px;
        margin: 8px 0;
    }
    .user-message {
        background-color: #E3F2FD;
        margin-left: auto;
        max-width: 80%;
    }
    .assistant-message {
        background-color: #F5F5F5;
        margin-right: auto;
        max-width: 80%;
    }
    a {
        color: #1E88E5;
        text-decoration: underline;
    }
    a:hover {
        color: #0D47A1;
    }
    """

    # 创建界面
    with gr.Blocks(
        title="律师 AI 助手",
        theme=gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="gray",
        ),
        css=custom_css,
    ) as interface:
        gr.Markdown(
            """
            # 🏛️ 律师 AI 助手

            基于 LLaMA-Factory 微调的 Qwen2.5-7B 法律大模型

            **功能特点：**
            - 📚 法律咨询与案例分析
            - 🔍 法规条文智能检索
            - 🔗 自动生成法规链接（点击即可跳转搜索引擎查询）
            - 💬 流畅的对话体验
            """
        )

        with gr.Row():
            with gr.Column(scale=4):
                chatbot = gr.Chatbot(
                    label="对话历史",
                    height=500,
                    show_copy_button=True,
                    bubble_full_width=False,
                )

                with gr.Row():
                    msg = gr.Textbox(
                        label="请输入您的问题",
                        placeholder="例如：什么是正当防卫？",
                        scale=4,
                        show_label=False,
                    )
                    submit = gr.Button("发送", variant="primary", scale=1)

                with gr.Row():
                    clear_btn = gr.Button("清空对话", variant="secondary")

                gr.Examples(
                    examples=[
                        "什么是正当防卫？",
                        "劳动合同解除的条件是什么？",
                        "请解释一下侵权责任法的基本原则",
                        "交通事故中的责任认定有哪些标准？",
                        "刑法中关于故意伤害罪的构成要件是什么？",
                    ],
                    inputs=msg,
                    label="示例问题",
                )

            with gr.Column(scale=1):
                gr.Markdown("### ⚙️ 参数设置")

                temperature = gr.Slider(
                    minimum=0.1,
                    maximum=2.0,
                    value=0.8,
                    step=0.1,
                    label="温度 (Temperature)",
                    info="值越低输出越确定，值越高输出越随机"
                )

                max_tokens = gr.Slider(
                    minimum=64,
                    maximum=1024,
                    value=512,
                    step=64,
                    label="最大生成长度 (Max Tokens)",
                    info="控制回复的最大长度"
                )

                gr.Markdown("### 📖 使用说明")
                gr.Markdown(
                    """
                    1. 在输入框中输入法律问题
                    2. 点击"发送"按钮或按回车键
                    3. 回复中的法规条文会自动添加超链接
                    4. 点击链接可在新窗口查看搜索结果
                    5. 可以随时清空对话历史
                    """
                )

                gr.Markdown("### 🔗 搜索引擎")
                gr.Markdown(
                    """
                    法规链接使用**百度搜索**，点击法规名称或法条号即可查询详细内容。
                    """
                )

        # 事件绑定
        submit.click(
            fn=app.chat,
            inputs=[msg, chatbot],
            outputs=[msg, chatbot],
        ).then(
            fn=lambda: "",
            outputs=msg,
        )

        msg.submit(
            fn=app.chat,
            inputs=[msg, chatbot],
            outputs=[msg, chatbot],
        ).then(
            fn=lambda: "",
            outputs=msg,
        )

        clear_btn.click(
            fn=app.clear_history,
            outputs=[chatbot],
        )

    return interface


if __name__ == "__main__":
    # 创建并启动界面
    interface = create_interface()

    # 启动 Gradio 应用
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
        quiet=False,
    )
