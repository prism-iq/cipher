#!/usr/bin/env python3
"""
SENSES - Minimal sensory daemon
OpenBSD style. Efficient. No CPU burn.

Audio: parec -> numpy FFT (low overhead)
Screen: grim on-demand only (60s interval)
Vision: disabled by default (enable with --vision)
"""

import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from threading import Thread, Event

# Config
HOME = Path.home()
BASE = HOME / "projects" / "cipher"
TARGETS = [BASE, HOME / "projects" / "nyx", HOME / "projects" / "geass"]

# Intervals (seconds)
AUDIO_INTERVAL = 0.5  # 2 Hz audio analysis (was 10 Hz - caused mouse freeze)
SCREEN_INTERVAL = 120 # 2 min between screenshots
VISION_INTERVAL = 300 # 5 min between camera captures (if enabled)
BROADCAST_THROTTLE = 1.0  # Max 1 write/sec to avoid I/O stall

# State
stop_event = Event()
last_broadcast = {}

def broadcast(sense: str, data: dict):
    """Write sense data to targets - throttled to avoid I/O stall"""
    now = time.time()
    if sense in last_broadcast and (now - last_broadcast[sense]) < BROADCAST_THROTTLE:
        return  # Throttled
    last_broadcast[sense] = now

    txt = json.dumps(data)
    for t in TARGETS:
        try:
            if t.exists():
                (t / f"{sense}.json").write_text(txt)
        except:
            pass

def get_audio_source() -> str:
    """Get best audio monitor source"""
    try:
        r = subprocess.run(["pactl", "list", "sources", "short"],
                          capture_output=True, text=True, timeout=3)
        lines = r.stdout.strip().split("\n")

        # Priority: easyeffects > ZenGo > any monitor
        for priority in ["easyeffects", "ZenGo"]:
            for line in lines:
                if priority in line and ".monitor" in line:
                    return line.split()[1]

        for line in lines:
            if ".monitor" in line:
                return line.split()[1]
    except:
        pass
    return ""

def audio_loop():
    """Audio analysis - efficient numpy FFT"""
    try:
        import numpy as np
    except ImportError:
        print("[!] numpy required")
        return

    source = get_audio_source()
    if not source:
        print("[!] No audio source")
        return

    print(f"[+] Audio: {source}")

    proc = subprocess.Popen(
        ["parec", "-d", source, "--rate=44100", "--channels=1", "--format=float32le"],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
    )

    chunk = 1024 * 4  # ~23ms at 44.1kHz
    prev_bass = 0.0

    while not stop_event.is_set():
        try:
            data = proc.stdout.read(chunk)
            if not data:
                break

            audio = np.frombuffer(data, dtype=np.float32)

            # RMS energy
            rms = float(np.sqrt(np.mean(audio ** 2)))
            energy = min(1.0, rms * 40)

            # Simple bass detection (no full FFT needed for vibe)
            # Low-pass via moving average
            kernel = 32
            if len(audio) > kernel:
                bass = float(np.mean(np.abs(audio[:len(audio)//4])))
                groove = min(1.0, abs(bass - prev_bass) * 20)
                prev_bass = bass * 0.7 + prev_bass * 0.3
            else:
                groove = 0.0

            vibe = "chill" if energy < 0.3 else "hype" if energy > 0.7 else "groovy"

            broadcast("music", {
                "energy": round(energy, 3),
                "groove": round(groove, 3),
                "vibe": vibe
            })

            time.sleep(AUDIO_INTERVAL)

        except Exception as e:
            if not stop_event.is_set():
                print(f"[!] Audio error: {e}")
            break

    proc.terminate()
    proc.wait()

def screen_loop():
    """Screenshot - infrequent, nice priority"""
    out = BASE / "vision"
    out.mkdir(parents=True, exist_ok=True)
    path = out / "screen.png"

    print(f"[+] Screen: {SCREEN_INTERVAL}s interval")

    while not stop_event.is_set():
        try:
            # No nice - causes core dump in sandbox (setpriority blocked)
            subprocess.run(
                ["grim", "-t", "png", "-q", "50", str(path)],
                timeout=10, capture_output=True, check=False
            )
            broadcast("screen", {"path": str(path), "ts": int(time.time())})
        except:
            pass

        # Wait with early exit check
        for _ in range(SCREEN_INTERVAL):
            if stop_event.is_set():
                break
            time.sleep(1)

def vision_loop():
    """Camera capture - very infrequent, optional"""
    out = BASE / "vision"
    out.mkdir(parents=True, exist_ok=True)
    path = out / "camera.jpg"

    print(f"[+] Vision: {VISION_INTERVAL}s interval")

    while not stop_event.is_set():
        try:
            # Single frame, low quality (no nice - blocked in sandbox)
            subprocess.run([
                "ffmpeg", "-y", "-f", "v4l2",
                "-video_size", "640x480",
                "-i", "/dev/video0",
                "-frames:v", "1",
                "-q:v", "10",
                str(path)
            ], timeout=10, capture_output=True, check=False)

            broadcast("vision", {"path": str(path), "ts": int(time.time())})
        except:
            pass

        for _ in range(VISION_INTERVAL):
            if stop_event.is_set():
                break
            time.sleep(1)

def main():
    enable_vision = "--vision" in sys.argv or "-v" in sys.argv

    def shutdown(sig, frame):
        print("\n[SENSES] Stopping...")
        stop_event.set()

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    print("[SENSES] Starting (OpenBSD style)...")

    threads = [
        Thread(target=audio_loop, daemon=True, name="audio"),
        Thread(target=screen_loop, daemon=True, name="screen"),
    ]

    if enable_vision:
        threads.append(Thread(target=vision_loop, daemon=True, name="vision"))

    for t in threads:
        t.start()

    # Wait for stop
    while not stop_event.is_set():
        time.sleep(1)

    # Grace period for threads
    time.sleep(0.5)
    print("[SENSES] Stopped")

if __name__ == "__main__":
    main()
