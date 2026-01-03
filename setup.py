"""
Lawyer AI - 基于微调大模型的法律问答系统
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="lawyer-ai",
    version="1.0.0",
    author="Project Team",
    author_email="",
    description="基于 LLaMA-Factory 微调的律师 AI 大模型应用",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/lawyer-ai",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "torch>=2.4.0",
        "transformers>=4.49.0",
        "accelerate>=1.3.0",
        "peft>=0.14.0",
        "trl>=0.8.6",
        "fastapi>=0.109.0",
        "uvicorn[standard]>=0.27.0",
        "gradio>=4.38.0",
        "pydantic>=2.0.0",
        "sse-starlette>=2.0.0",
        "pyyaml>=6.0",
    ],
)
