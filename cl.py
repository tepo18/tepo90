#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import threading
import time
import requests
import base64
import urllib.parse
import socket
from typing import List
from concurrent.futures import ThreadPoolExecutor

# ===================== تنظیمات =====================
TEXT_PATH = "normal.txt"
FIN_PATH = "final.txt"

LINK_PATH = [
    "https://old-limit-e122-edge-333.ahsan-tepo1383online.workers.dev/sub?token=8bfaf9cc1c81e4005289b8d8c738077c",
    "https://raw.githubusercontent.com/patterniha/Free-Configs/refs/heads/main/configs_base64.txt",
    "https://xnzvhfevu8ms.shah98-tepo98.workers.dev/feed/ZEUS-77IELBGK",
    "https://wlzmgdefumms.ahsan-tepo1390.workers.dev/feed/ZEUS-TBAITSU1",
    "https://uxzp6qeuunos.shah-tepo98.workers.dev/feed/98PEZY4V",
    "https://uxzp6qeuunos.shah-tepo98.workers.dev/feed/X3R0LMNT",
    "https://uxzp6qeuunos.shah-tepo98.workers.dev/feed/tepo98",
]

FILE_HEADER_TEXT = "//profile-title: base64:2YfZhduM2LTZhyDZgdi52KfZhCDwn5iO8J+YjvCfmI4gaGFtZWRwNzE="

# ===================== توابع =====================

def fetch_link(url: str) -> List[str]:
    try:
        r = requests.get(url, timeout=15)

        if r.status_code == 200:
            lines = r.text.splitlines()
            return [l.strip() for l in lines if l.strip()]

    except Exception as e:
        print(f"[⚠️] Cannot fetch {url}: {e}")

    return []


def is_valid_config(line: str) -> bool:
    line = line.strip()

    if not line or len(line) < 5:
        return False

    lower = line.lower()

    if "pin=0" in lower or "pin=red" in lower or "pin=قرمز" in lower:
        return False

    return True


def parse_config_line(line: str):
    try:
        line = urllib.parse.unquote(line.strip())

        for p in [
            "vmess",
            "vless",
            "trojan",
            "hy2",
            "hysteria2",
            "ss",
            "socks",
            "wireguard"
        ]:
            if line.startswith(p + "://"):
                return line

    except Exception:
        pass

    return None


def extract_host_port(cfg: str):
    """
    استخراج Host و Port
    پشتیبانی از:
    - hostname
    - IPv4
    - IPv6
    - پورت مشخص
    - پورت بدون مقدار که در آن 443 استفاده می‌شود
    """

    try:
        parsed = urllib.parse.urlsplit(cfg)

        host = parsed.hostname
        port = parsed.port

        if host:
            return host, port if port else 443

    except Exception:
        pass

    # fallback برای فرمت‌هایی که urlsplit نتواند parse کند
    try:
        import re

        # IPv6 داخل براکت
        m = re.search(
            r"@\[([0-9a-fA-F:]+)\](?::(\d+))?",
            cfg
        )

        if m:
            host = m.group(1)
            port = int(m.group(2)) if m.group(2) else 443
            return host, port

        # hostname / IPv4
        m = re.search(
            r"@([^:/?#]+)(?::(\d+))?",
            cfg
        )

        if m:
            host = m.group(1)
            port = int(m.group(2)) if m.group(2) else 443
            return host, port

    except Exception:
        pass

    return "", 443


def tcp_test(host: str, port: int, timeout=3) -> bool:
    try:
        with socket.create_connection(
            (host, port),
            timeout=timeout
        ):
            return True

    except Exception:
        return False


def process_configs(
    lines: List[str],
    precise_test=False
) -> List[str]:

    valid_configs = []
    lock = threading.Lock()

    def worker(line):
        cfg = parse_config_line(line)
        passed = False

        if cfg:
            try:
                host, port = extract_host_port(cfg)

                if precise_test and host:
                    passed = tcp_test(
                        host,
                        port
                    )
                else:
                    passed = True

            except Exception:
                passed = False

        if passed and is_valid_config(line):
            with lock:
                valid_configs.append(line)

    # محدود کردن تعداد Threadها
    max_workers = min(
        32,
        max(1, len(lines))
    )

    with ThreadPoolExecutor(
        max_workers=max_workers
    ) as executor:
        list(executor.map(worker, lines))

    # حذف تکراری‌ها
    final_list = list(
        dict.fromkeys(valid_configs)
    )

    return final_list


def save_outputs(lines: List[str]):
    try:
        # ابتدا فایل‌ها را خالی می‌کنیم
        with open(
            TEXT_PATH,
            "w",
            encoding="utf-8"
        ) as f:
            f.write("")

        with open(
            FIN_PATH,
            "w",
            encoding="utf-8"
        ) as f:
            f.write("")

        # ===================== مرحله نرمال =====================

        normal_lines = lines

        with open(
            TEXT_PATH,
            "w",
            encoding="utf-8"
        ) as f:
            f.write(
                "\n".join(
                    [FILE_HEADER_TEXT] + normal_lines
                )
            )

        print(
            f"[ℹ️] Stage 1: "
            f"{len(normal_lines)} configs saved to {TEXT_PATH}"
        )

        # ===================== مرحله فینال =====================

        final_lines = process_configs(
            normal_lines,
            precise_test=True
        )

        with open(
            FIN_PATH,
            "w",
            encoding="utf-8"
        ) as f:
            f.write(
                "\n".join(final_lines)
            )

        print(
            f"[ℹ️] Stage 2: "
            f"{len(final_lines)} configs saved to {FIN_PATH}"
        )

        print(
            f"[✅] Update complete. "
            f"Total sources: {len(lines)}"
        )

        print(
            f"  -> Normal configs: "
            f"{len(normal_lines)}"
        )

        print(
            f"  -> Final configs: "
            f"{len(final_lines)}"
        )

    except Exception as e:
        print(
            f"[❌] Error saving files: {e}"
        )


def update_subs():
    all_lines = []

    for url in LINK_PATH:

        fetched = fetch_link(url)

        if not fetched:
            print(
                f"[⚠️] Cannot fetch or empty source: "
                f"{url}"
            )

        else:
            all_lines.extend(fetched)

    print(
        f"[*] Total lines fetched from sources: "
        f"{len(all_lines)}"
    )

    all_lines = process_configs(
        all_lines
    )

    save_outputs(
        all_lines
    )


# ===================== اجرای دستی =====================

if __name__ == "__main__":

    print(
        "[*] Starting manual subscription update..."
    )

    update_subs()

    print(
        "[*] Done. Run this script manually whenever needed."
    )
