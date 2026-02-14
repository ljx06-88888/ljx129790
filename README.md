# 网络分析工具

一个轻量的命令行网络分析工具，支持：

- **设备扫描**：扫描局域网内在线设备，展示 IP、MAC、主机名、厂商、设备类型（型号提示）。
- **信道扫描**：扫描附近 Wi-Fi AP，展示 SSID、BSSID、信道、频率、信号，并统计信道占用情况。

## 依赖

- Python 3.10+
- `nmap`（用于设备扫描）
- `nmcli`（用于 Wi-Fi 信道扫描，通常由 NetworkManager 提供）

## 使用方法

### 1) 扫描局域网设备

```bash
python3 network_analyzer.py scan-devices --subnet 192.168.1.0/24
```

JSON 输出：

```bash
python3 network_analyzer.py scan-devices --subnet 192.168.1.0/24 --json
```

### 2) 扫描 Wi-Fi 信道

```bash
python3 network_analyzer.py scan-channels
```

指定网卡：

```bash
python3 network_analyzer.py scan-channels --interface wlan0
```

JSON 输出：

```bash
python3 network_analyzer.py scan-channels --json
```

## 打包为 Windows `.exe`

> 说明：要得到真正的 Windows `.exe`，建议在 **Windows 环境** 打包。

### 本地 Windows 打包

1. 安装 Python（建议 3.10+）。
2. 在项目目录执行：

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements-build.txt
pyinstaller --onefile --name network_analyzer.exe network_analyzer.py
```

生成文件位置：

```text
dist\network_analyzer.exe
```

### GitHub Actions 自动构建 `.exe`

本仓库已提供 Windows 构建工作流：

- 文件：`.github/workflows/build-windows-exe.yml`
- 触发：手动触发（`workflow_dispatch`）
- 产物：`network-analyzer-windows-exe`（下载后即可获得 `network_analyzer.exe`）

## 说明

- 设备“型号”来自 `nmap` 的 `Device type` 信息，准确性取决于目标设备和网络环境。
- 扫描局域网设备通常需要管理员权限（例如使用 `sudo`）。
- 无线信道扫描依赖系统网络管理能力与无线网卡权限。
