# 可部署的 AI 环境空间（Docker Compose）

这个仓库提供了一个**开箱即用的本地 AI 环境空间**，包含：

- **code-server**：在线 VS Code 开发环境
- **JupyterLab**：数据科学/训练实验环境
- **Ollama**：本地大模型推理服务
- **Open WebUI**：可视化聊天与模型交互界面

---

## 1. 前置要求

- 已安装 Docker
- 已安装 Docker Compose（Docker Desktop 通常已内置）

可用以下命令检查：

```bash
docker --version
docker compose version
```

---

## 2. 快速启动

```bash
chmod +x scripts/bootstrap.sh
./scripts/bootstrap.sh
```

脚本会自动：

1. 复制 `.env.example` 为 `.env`（如果 `.env` 不存在）
2. 创建数据目录（`workspace/`, `ollama/`, `open-webui/`）
3. 后台启动全部服务

---

## 3. 默认访问地址

- code-server: `http://localhost:8080`
- JupyterLab: `http://localhost:8888`
- Open WebUI: `http://localhost:3000`
- Ollama API: `http://localhost:11434`

默认密码/令牌请在 `.env` 中修改：

- `CODE_SERVER_PASSWORD`
- `JUPYTER_TOKEN`
- `WEBUI_SECRET_KEY`

---

## 4. 常用命令

### 查看容器状态

```bash
docker compose ps
```

### 查看日志

```bash
docker compose logs -f
```

### 停止环境

```bash
docker compose down
```

### 拉取模型（示例）

```bash
docker exec -it ai-ollama ollama pull qwen2.5:7b
```

---

## 5. 目录说明

- `docker-compose.yml`：核心服务编排
- `.env.example`：环境变量模板
- `scripts/bootstrap.sh`：一键初始化 + 启动脚本
- `workspace/`：开发与实验代码目录（挂载给 code-server/Jupyter）
- `ollama/`：Ollama 模型与缓存数据
- `open-webui/`：Open WebUI 持久化数据

---

## 6. 可选增强建议

- 增加 `nginx + https` 做反向代理与证书
- 为 `workspace` 添加项目模板（RAG、Agent、微调脚本）
- 在 `docker-compose.yml` 中接入向量数据库（Qdrant/Weaviate）
- 使用 `.env` 配置代理与镜像加速，提高拉镜像和下载模型速度
