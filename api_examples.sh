#!/bin/bash
# API 调用示例脚本

API_BASE="http://localhost:8000"

echo "=========================================="
echo "律师 AI 大模型 API 调用示例"
echo "=========================================="
echo ""

# 示例 1：健康检查
echo "1. 健康检查"
echo "curl $API_BASE/health"
echo ""
curl -s "$API_BASE/health" | python3 -m json.tool
echo ""
echo ""

# 示例 2：获取模型信息
echo "2. 获取模型信息"
echo "curl $API_BASE/v1/model/info"
echo ""
curl -s "$API_BASE/v1/model/info" | python3 -m json.tool
echo ""
echo ""

# 示例 3：对话补全
echo "3. 对话补全"
echo "curl -X POST \"$API_BASE/v1/chat/completions\" \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{"
echo "    \"messages\": [{\"role\": \"user\", \"content\": \"什么是正当防卫？\"}],"
echo "    \"temperature\": 0.8,"
echo "    \"max_tokens\": 512,"
echo "    \"enable_law_links\": true"
echo "  }'"
echo ""

curl -X POST "$API_BASE/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "什么是正当防卫？"}],
    "temperature": 0.8,
    "max_tokens": 512,
    "enable_law_links": true
  }' | python3 -m json.tool
echo ""
echo ""

# 示例 4：多轮对话
echo "4. 多轮对话"
echo "curl -X POST \"$API_BASE/v1/chat/completions\" \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{"
echo "    \"messages\": ["
echo "      {\"role\": \"user\", \"content\": \"什么是正当防卫？\"},"
echo "      {\"role\": \"assistant\", \"content\": \"正当防卫是指为了使国家、公共利益...\"},"
echo "      {\"role\": \"user\", \"content\": \"那什么是防卫过当呢？\"}"
echo "    ],"
echo "    \"temperature\": 0.8,"
echo "    \"max_tokens\": 512"
echo "  }'"
echo ""

curl -X POST "$API_BASE/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "什么是正当防卫？"},
      {"role": "assistant", "content": "正当防卫是指为了使国家、公共利益、本人或者他人的人身、财产和其他权利免受正在进行的不法侵害，而采取的制止不法侵害的行为。"},
      {"role": "user", "content": "那什么是防卫过当呢？"}
    ],
    "temperature": 0.8,
    "max_tokens": 512
  }' | python3 -m json.tool
echo ""
echo ""

# 示例 5：法规分析
echo "5. 法规分析"
echo "curl -X POST \"$API_BASE/v1/chat/analyze\" \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '["
echo "    {\"role\": \"user\", \"content\": \"根据刑法第二十条\"},"
echo "    {\"role\": \"assistant\", \"content\": \"根据《民法典》第一千零七十八条的规定...\"}"
echo "  ]'"
echo ""

curl -X POST "$API_BASE/v1/chat/analyze" \
  -H "Content-Type: application/json" \
  -d '[
    {"role": "user", "content": "根据刑法第二十条"},
    {"role": "assistant", "content": "根据《民法典》第一千零七十八条的规定..."}
  ]' | python3 -m json.tool
echo ""
echo ""

echo "=========================================="
echo "示例完成"
echo "=========================================="
echo ""
echo "提示：确保 API 服务已启动（./start.sh api）"
echo "API 文档：http://localhost:8000/docs"
