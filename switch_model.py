#!/usr/bin/env python3
"""
模型切换工具
用于在不同训练的模型之间快速切换
"""

import argparse
import os
import sys
from pathlib import Path

import yaml

# 配置文件路径
CONFIG_FILE = Path(__file__).parent / "config_models.yaml"
APP_PY = Path(__file__).parent / "app.py"
API_SERVER_PY = Path(__file__).parent / "api_server.py"


def load_config():
    """加载配置文件"""
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def save_config(config):
    """保存配置文件"""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False)


def list_models():
    """列出所有可用模型"""
    config = load_config()
    models = config.get('models', {})
    current = config.get('current_model', '')

    print("=" * 60)
    print("可用模型列表：")
    print("=" * 60)

    for model_id, model_config in models.items():
        is_current = model_id == current
        marker = "【当前】" if is_current else ""
        print(f"\n{model_id} {marker}")
        print(f"  名称: {model_config['name']}")
        print(f"  基础模型: {model_config['model_name_or_path']}")
        print(f"  LoRA 权重: {model_config.get('adapter_name_or_path', '无')}")
        print(f"  模板: {model_config['template']}")
        print(f"  微调类型: {model_config['finetuning_type']}")
        print(f"  描述: {model_config['description']}")

    print("\n" + "=" * 60)
    print(f"当前使用: {current}")
    print("=" * 60)


def switch_model(model_id):
    """切换模型"""
    config = load_config()
    models = config.get('models', {})

    if model_id not in models:
        print(f"❌ 错误: 模型 '{model_id}' 不存在")
        print(f"\n可用模型: {', '.join(models.keys())}")
        sys.exit(1)

    # 更新当前模型
    config['current_model'] = model_id
    save_config(config)

    model_config = models[model_id]

    print("=" * 60)
    print(f"✅ 已切换到模型: {model_id}")
    print("=" * 60)
    print(f"  模型名称: {model_config['name']}")
    print(f"  基础模型: {model_config['model_name_or_path']}")
    print(f"  LoRA 权重: {model_config.get('adapter_name_or_path', '无')}")
    print(f"  描述: {model_config['description']}")
    print("=" * 60)
    print("\n📝 配置已更新！")
    print("请重启应用以使用新模型：")
    print("  ./start.sh gradio   # Gradio 界面")
    print("  ./start.sh api      # API 服务")


def add_model(model_id, name, base_model, adapter_path, template="Qwen", finetuning_type="lora", description=""):
    """添加新模型配置"""
    config = load_config()

    if 'models' not in config:
        config['models'] = {}

    if model_id in config['models']:
        print(f"⚠️  警告: 模型 '{model_id}' 已存在，将被覆盖")

    config['models'][model_id] = {
        'name': name,
        'model_name_or_path': base_model,
        'adapter_name_or_path': adapter_path,
        'template': template,
        'finetuning_type': finetuning_type,
        'description': description
    }

    save_config(config)

    print(f"✅ 模型 '{model_id}' 已添加")


def compare_models(model1_id, model2_id):
    """对比两个模型"""
    config = load_config()
    models = config.get('models', {})

    for mid in [model1_id, model2_id]:
        if mid not in models:
            print(f"❌ 错误: 模型 '{mid}' 不存在")
            sys.exit(1)

    m1 = models[model1_id]
    m2 = models[model2_id]

    print("=" * 80)
    print(f"模型对比: {model1_id} vs {model2_id}")
    print("=" * 80)

    print(f"\n{model1_id.upper()}:")
    print(f"  名称: {m1['name']}")
    print(f"  基础模型: {m1['model_name_or_path']}")
    print(f"  LoRA 权重: {m1.get('adapter_name_or_path', '无')}")
    print(f"  描述: {m1['description']}")

    print(f"\n{model2_id.upper()}:")
    print(f"  名称: {m2['name']}")
    print(f"  基础模型: {m2['model_name_or_path']}")
    print(f"  LoRA 权重: {m2.get('adapter_name_or_path', '无')}")
    print(f"  描述: {m2['description']}")

    print("\n" + "=" * 80)
    print("💡 使用建议:")
    print("=" * 80)

    # 简单的对比逻辑
    if "7B" in m1['name'] and "1.5B" in m2['name']:
        print(f"  • {model1_id}: 性能更强，回答更准确，但推理速度较慢")
        print(f"  • {model2_id}: 速度更快，响应更及时，但可能准确度稍低")
    elif "1.5B" in m1['name'] and "7B" in m2['name']:
        print(f"  • {model1_id}: 速度更快，响应更及时，但可能准确度稍低")
        print(f"  • {model2_id}: 性能更强，回答更准确，但推理速度较慢")
    else:
        print(f"  • {model1_id}: {m1['description']}")
        print(f"  • {model2_id}: {m2['description']}")

    print(f"\n🧪 建议: 可以在相同问题下对比两个模型的回答质量")


def get_current_model_config():
    """获取当前模型配置（用于 app.py 和 api_server.py）"""
    config = load_config()
    current_id = config.get('current_model', 'qwen-7b')
    models = config.get('models', {})

    if current_id not in models:
        print(f"⚠️  警告: 当前模型 '{current_id}' 不存在，使用默认配置")
        return {}

    return models[current_id]


def main():
    parser = argparse.ArgumentParser(description='模型切换工具')
    subparsers = parser.add_subparsers(dest='command', help='子命令')

    # list 命令
    subparsers.add_parser('list', help='列出所有可用模型')

    # switch 命令
    switch_parser = subparsers.add_parser('switch', help='切换模型')
    switch_parser.add_argument('model_id', help='模型 ID')

    # compare 命令
    compare_parser = subparsers.add_parser('compare', help='对比两个模型')
    compare_parser.add_argument('model1', help='第一个模型 ID')
    compare_parser.add_argument('model2', help='第二个模型 ID')

    # add 命令
    add_parser = subparsers.add_parser('add', help='添加新模型')
    add_parser.add_argument('--id', required=True, help='模型 ID')
    add_parser.add_argument('--name', required=True, help='模型名称')
    add_parser.add_argument('--base', required=True, help='基础模型路径')
    add_parser.add_argument('--adapter', help='LoRA 权重路径')
    add_parser.add_argument('--template', default='Qwen', help='模板类型')
    add_parser.add_argument('--finetuning', default='lora', help='微调类型')
    add_parser.add_argument('--desc', default='', help='模型描述')

    args = parser.parse_args()

    if args.command == 'list':
        list_models()
    elif args.command == 'switch':
        switch_model(args.model_id)
    elif args.command == 'compare':
        compare_models(args.model1, args.model2)
    elif args.command == 'add':
        add_model(
            args.id, args.name, args.base, args.adapter,
            args.template, args.finetuning, args.desc
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
