#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import json
import base64
import threading
import urllib.request
import subprocess
import platform
import re

# ---------------- مسیر فایل‌ها ----------------
TEXT_NORMAL = "normal.txt"
TEXT_FINAL = "final.txt"

# ---------------- منابع ----------------
LINKS = [
    "https://raw.githubusercontent.com/tepo18/tepo90/main/tepo10.txt",
    "https://raw.githubusercontent.com/tepo18/tepo90/main/tepo20.txt",
    "https://raw.githubusercontent.com/tepo18/tepo90/main/tepo30.txt",
    "https://raw.githubusercontent.com/tepo18/tepo90/main/tepo40.txt",
    "https://raw.githubusercontent.com/tepo18/tepo90/main/tepo50.txt",
]

# ---------------- پینگ واقعی ----------------
def ping(host: str, count: int = 1, timeout: int = 1) -> float:
    param_count = "-n" if platform.system().lower() == "windows" else "-c"
    param_timeout = "-w" if platform.system().lower() == "windows" else "-W"
    try:
        result = subprocess.run(
            ["ping", param_count, str(count), param_timeout, str(timeout), host],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        match = re.search(r'time[=<]\s*(\d+\.?\d*)', result.stdout)
        if match:
            return float(match.group(1))
    except:
        pass
    return float('inf')

# ---------------- خواندن منابع ----------------
def fetch_lines(url):
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            data = resp.read().decode(errors="ignore")
            return [line.strip() for line in data.splitlines() if line.strip()]
    except Exception as e:
        print(f"[ERROR] Cannot fetch {url}: {e}")
        return []

# ---------------- استخراج host ----------------
def get_host(line):
    try:
        if line.startswith("vmess://"):
            b64 = line[8:].split('#')[0]
            missing_padding = len(b64) % 4
            if missing_padding: b64 += '=' * (4 - missing_padding)
            js = json.loads(base64.b64decode(b64).decode('utf-8'))
            host = js.get("add") or js.get("host")
            return host
        elif line.startswith("vless://") or line.startswith("trojan://") or line.startswith("ss://"):
            return line.split("@")[1].split(":")[0]
        else:
            return None
    except:
        return None

# ---------------- پردازش پینگ اولیه ----------------
def first_ping(lines):
    results = []
    lock = threading.Lock()
    threads = []

    def worker(line):
        host = get_host(line)
        if host:
            p = ping(host)
            if p < float('inf'):
                with lock:
                    results.append((line, p))

    for line in lines:
        t = threading.Thread(target=worker, args=(line,))
        t.start()
        threads.append(t)
        if len(threads) >= 20:
            for th in threads: th.join()
            threads = []

    for th in threads: th.join()

    unique = {}
    for line, p in results:
        if line not in unique:
            unique[line] = p

    sorted_lines = sorted(unique.keys(), key=lambda x: unique[x])
    return sorted_lines

# ---------------- پردازش پینگ دقیق ----------------
def detailed_ping(lines, max_ping=1200):
    results = []
    lock = threading.Lock()
    threads = []

    def worker(line):
        host = get_host(line)
        if host:
            p = ping(host, count=3, timeout=2)  # چندبار پینگ برای پایدارتر بودن
            if p <= max_ping:
                with lock:
                    results.append((line, p))

    for line in lines:
        t = threading.Thread(target=worker, args=(line,))
        t.start()
        threads.append(t)
        if len(threads) >= 20:
            for th in threads: th.join()
            threads = []

    for th in threads: th.join()

    unique = {}
    for line, p in results:
        if line not in unique:
            unique[line] = p

    sorted_lines = sorted(unique.keys(), key=lambda x: unique[x])
    return sorted_lines

# ---------------- ذخیره فایل ----------------
def save_file(path, lines):
    with open(path, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")
    print(f"[INFO] Saved {len(lines)} configs to {path}")

# ---------------- بروزرسانی ----------------
def update_all():
    print("[*] Fetching sources...")
    all_lines = []
    for link in LINKS:
        all_lines.extend(fetch_lines(link))
    print(f"[*] Total lines fetched: {len(all_lines)}")

    print("[*] Stage 1: First ping check (basic filtering)...")
    normal_lines = first_ping(all_lines)
    save_file(TEXT_NORMAL, normal_lines)

    print("[*] Stage 2: Detailed ping stability check...")
    final_lines = detailed_ping(normal_lines)
    save_file(TEXT_FINAL, final_lines)

# ---------------- حلقه بروزرسانی خودکار ----------------
if __name__ == "__main__":
    print("[*] Starting auto-updater with two-stage ping...")
    while True:
        start_time = time.time()
        update_all()
        elapsed = time.time() - start_time
        print(f"[*] Update complete. Next update in 1 hour. Elapsed: {elapsed:.2f}s\n")
        time.sleep(3600)
