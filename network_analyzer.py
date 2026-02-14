#!/usr/bin/env python3
"""Network analysis utility.

Features:
1. Discover devices in local network and display device name/model hints.
2. Scan Wi-Fi channels and summarize channel utilization.
"""

from __future__ import annotations

import argparse
import ipaddress
import json
import re
import shutil
import socket
import subprocess
from collections import Counter
from dataclasses import dataclass
from typing import Iterable


@dataclass
class DeviceInfo:
    ip: str
    mac: str
    hostname: str
    vendor: str
    model: str


@dataclass
class ChannelInfo:
    ssid: str
    bssid: str
    channel: int
    frequency_mhz: int
    signal_dbm: int | None


def run_cmd(cmd: list[str]) -> str:
    """Run command and return stdout; raise RuntimeError when command fails."""
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True)
    except FileNotFoundError as exc:
        raise RuntimeError(f"命令不存在: {' '.join(cmd)}") from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"命令执行失败: {' '.join(cmd)}\n{exc.output}") from exc
    return out


def hostname_for_ip(ip: str) -> str:
    try:
        return socket.gethostbyaddr(ip)[0]
    except (socket.herror, socket.gaierror, OSError):
        return "-"


def parse_nmap_devices(nmap_output: str) -> list[DeviceInfo]:
    devices: list[DeviceInfo] = []
    blocks = re.split(r"\nNmap scan report for ", "\n" + nmap_output)
    for block in blocks[1:]:
        lines = block.splitlines()
        header = lines[0].strip()
        ip_match = re.search(r"(\d+\.\d+\.\d+\.\d+)$", header)
        if not ip_match:
            continue
        ip = ip_match.group(1)
        mac = "-"
        vendor = "-"
        model = "-"

        mac_line = next((line for line in lines if "MAC Address:" in line), "")
        mac_match = re.search(r"MAC Address:\s*([0-9A-F:]{17})(?:\s*\((.+?)\))?", mac_line)
        if mac_match:
            mac = mac_match.group(1)
            vendor = mac_match.group(2) or "-"

        os_line = next((line for line in lines if line.startswith("Device type:")), "")
        if os_line:
            model = os_line.split(":", 1)[1].strip() or "-"

        hostname = hostname_for_ip(ip)
        devices.append(DeviceInfo(ip=ip, mac=mac, hostname=hostname, vendor=vendor, model=model))
    return devices


def discover_devices(subnet: str) -> list[DeviceInfo]:
    """Discover devices via nmap. Requires nmap installed."""
    ipaddress.ip_network(subnet, strict=False)
    if not shutil.which("nmap"):
        raise RuntimeError("未找到 nmap，请先安装 nmap。")

    output = run_cmd(["nmap", "-sn", "-O", subnet])
    return parse_nmap_devices(output)


def parse_nmcli_channels(raw: str) -> list[ChannelInfo]:
    channels: list[ChannelInfo] = []
    for line in raw.splitlines():
        if not line.strip():
            continue
        fields = line.split(":")
        if len(fields) < 5:
            continue
        ssid, bssid, freq, chan, signal = fields[:5]
        channel = int(chan) if chan.isdigit() else -1
        frequency = int(freq) if freq.isdigit() else -1
        sig = int(signal) if signal.lstrip("-").isdigit() else None
        channels.append(
            ChannelInfo(
                ssid=ssid or "<hidden>",
                bssid=bssid,
                channel=channel,
                frequency_mhz=frequency,
                signal_dbm=sig,
            )
        )
    return channels


def scan_channels(interface: str | None = None) -> list[ChannelInfo]:
    """Scan nearby Wi-Fi AP channels using nmcli."""
    if not shutil.which("nmcli"):
        raise RuntimeError("未找到 nmcli，请安装 NetworkManager 工具。")

    cmd = ["nmcli", "-t", "-f", "SSID,BSSID,FREQ,CHAN,SIGNAL", "dev", "wifi", "list"]
    if interface:
        cmd.extend(["ifname", interface])
    output = run_cmd(cmd)
    return parse_nmcli_channels(output)


def print_device_table(devices: Iterable[DeviceInfo]) -> None:
    headers = ["IP", "MAC", "主机名", "厂商", "设备型号/类型"]
    widths = [15, 17, 30, 24, 20]
    line_fmt = " ".join(f"{{:<{w}}}" for w in widths)
    print(line_fmt.format(*headers))
    print("-" * (sum(widths) + len(widths) - 1))
    for d in devices:
        print(line_fmt.format(d.ip, d.mac, d.hostname[:30], d.vendor[:24], d.model[:20]))


def print_channel_table(channels: Iterable[ChannelInfo]) -> None:
    channels = list(channels)
    headers = ["SSID", "BSSID", "信道", "频率(MHz)", "信号"]
    widths = [24, 20, 6, 10, 6]
    line_fmt = " ".join(f"{{:<{w}}}" for w in widths)
    print(line_fmt.format(*headers))
    print("-" * (sum(widths) + len(widths) - 1))
    for c in channels:
        signal = str(c.signal_dbm) if c.signal_dbm is not None else "-"
        print(line_fmt.format(c.ssid[:24], c.bssid[:20], c.channel, c.frequency_mhz, signal))

    usage = Counter(c.channel for c in channels if c.channel > 0)
    if usage:
        print("\n信道占用统计:")
        for channel, count in sorted(usage.items()):
            print(f"  信道 {channel:>2}: {count} 个AP")


def to_json(data: Iterable[DeviceInfo] | Iterable[ChannelInfo]) -> str:
    return json.dumps([item.__dict__ for item in data], ensure_ascii=False, indent=2)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="网络分析工具：设备识别 + Wi-Fi信道扫描")
    sub = parser.add_subparsers(dest="command", required=True)

    scan_dev = sub.add_parser("scan-devices", help="扫描子网内在线设备")
    scan_dev.add_argument("--subnet", required=True, help="CIDR 子网，例如 192.168.1.0/24")
    scan_dev.add_argument("--json", action="store_true", help="JSON 输出")

    scan_chan = sub.add_parser("scan-channels", help="扫描附近 Wi-Fi 信道")
    scan_chan.add_argument("--interface", help="无线网卡名，例如 wlan0")
    scan_chan.add_argument("--json", action="store_true", help="JSON 输出")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.command == "scan-devices":
        devices = discover_devices(args.subnet)
        if args.json:
            print(to_json(devices))
        else:
            print_device_table(devices)
    elif args.command == "scan-channels":
        channels = scan_channels(args.interface)
        if args.json:
            print(to_json(channels))
        else:
            print_channel_table(channels)


if __name__ == "__main__":
    main()
