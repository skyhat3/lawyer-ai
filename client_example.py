#!/usr/bin/env python3
"""
FastAPI 客户端示例
演示如何调用律师 AI 助手 API
"""

import requests
import json
from typing import List, Dict


class LawyerAIClient:
    """律师 AI 助手 API 客户端"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        初始化客户端

        Args:
            base_url: API 基础地址
        """
        self.base_url = base_url.rstrip('/')
        self.api_base = f"{self.base_url}/v1"

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.8,
        max_tokens: int = 512,
        top_p: float = 0.9,
        enable_law_links: bool = True
    ) -> Dict:
        """
        发起对话请求

        Args:
            messages: 对话历史
            temperature: 温度参数
            max_tokens: 最大生成长度
            top_p: Top-p 采样参数
            enable_law_links: 是否启用法规超链接

        Returns:
            API 响应
        """
        url = f"{self.api_base}/chat/completions"

        payload = {
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "enable_law_links": enable_law_links
        }

        try:
            response = requests.post(url, json=payload, timeout=300)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            return None

    def analyze_law_references(self, messages: List[Dict[str, str]]) -> Dict:
        """
        分析法规引用

        Args:
            messages: 对话历史

        Returns:
            法规引用列表
        """
        url = f"{self.api_base}/chat/analyze"

        try:
            response = requests.post(url, json=messages, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            return None

    def get_model_info(self) -> Dict:
        """
        获取模型信息

        Returns:
            模型信息
        """
        url = f"{self.api_base}/model/info"

        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            return None

    def health_check(self) -> bool:
        """
        健康检查

        Returns:
            服务是否健康
        """
        url = f"{self.base_url}/health"

        try:
            response = requests.get(url, timeout=5)
            return response.status_code == 200 and response.json().get("model_loaded", False)
        except requests.exceptions.RequestException:
            return False


def main():
    """主函数 - 演示客户端使用"""

    # 初始化客户端
    client = LawyerAIClient()

    # 健康检查
    print("正在检查服务状态...")
    if not client.health_check():
        print("❌ 服务未就绪，请先启动 API 服务器")
        return
    print("✅ 服务正常运行\n")

    # 获取模型信息
    print("=" * 60)
    print("模型信息")
    print("=" * 60)
    model_info = client.get_model_info()
    if model_info:
        print(f"模型名称: {model_info.get('model_name')}")
        print(f"基础模型: {model_info.get('base_model')}")
        print(f"微调类型: {model_info.get('finetuning_type')}")
        print(f"描述: {model_info.get('description')}")
        print(f"功能: {', '.join(model_info.get('capabilities', []))}")
    print()

    # 示例对话
    examples = [
        "什么是正当防卫？",
        "劳动合同解除的条件是什么？",
        "请解释一下侵权责任法的基本原则",
        "交通事故中的责任认定有哪些标准？"
    ]

    print("=" * 60)
    print("开始对话（输入 'quit' 退出）")
    print("=" * 60)
    print()

    conversation_history = []

    # 先运行几个示例
    for i, question in enumerate(examples[:2], 1):
        print(f"\n--- 示例 {i} ---")
        print(f"用户: {question}")

        # 构建消息
        messages = [{"role": "user", "content": question}]

        # 调用 API
        response = client.chat(messages)

        if response:
            print(f"助手: {response.get('content')}")
            print()

            # 显示法规引用
            law_refs = response.get('law_references', [])
            if law_refs:
                print("📚 检测到的法规引用:")
                for ref in law_refs:
                    print(f"  - {ref['text']}: {ref['link']}")
                print()

            conversation_history.extend([
                {"role": "user", "content": question},
                {"role": "assistant", "content": response.get('content')}
            ])
        else:
            print("❌ 请求失败")

    # 交互式对话
    while True:
        try:
            user_input = input("\n用户: ").strip()

            if user_input.lower() in ['quit', 'exit', '退出']:
                print("再见！")
                break

            if not user_input:
                continue

            # 添加用户消息
            conversation_history.append({"role": "user", "content": user_input})

            # 调用 API
            print("助手: ", end="", flush=True)
            response = client.chat(conversation_history)

            if response:
                print(response.get('content'))

                # 显示法规引用
                law_refs = response.get('law_references', [])
                if law_refs:
                    print("\n📚 检测到的法规引用:")
                    for ref in law_refs:
                        print(f"  - {ref['text']}: {ref['link']}")

                # 添加助手回复
                conversation_history.append({
                    "role": "assistant",
                    "content": response.get('content')
                })
            else:
                print("❌ 请求失败")

        except KeyboardInterrupt:
            print("\n\n再见！")
            break
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")


if __name__ == "__main__":
    main()
