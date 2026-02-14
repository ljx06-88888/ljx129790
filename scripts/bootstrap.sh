#!/usr/bin/env bash
set -euo pipefail

if [ ! -f .env ]; then
  cp .env.example .env
  echo "[INFO] 未检测到 .env，已根据 .env.example 自动生成。"
fi

mkdir -p workspace ollama open-webui

echo "[INFO] 启动 AI 环境空间..."
docker compose up -d

echo "[INFO] 启动完成。访问地址："
echo "- code-server: http://localhost:${CODE_SERVER_PORT:-8080}"
echo "- JupyterLab:  http://localhost:${JUPYTER_PORT:-8888}"
echo "- Open WebUI:  http://localhost:${OPEN_WEBUI_PORT:-3000}"
echo ""
echo "[TIP] 首次使用 Ollama 拉取模型示例："
echo "docker exec -it ai-ollama ollama pull qwen2.5:7b"
