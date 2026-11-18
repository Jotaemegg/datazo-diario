"""Imprime los tramos de voz (separados por pausas) para sincronizar escenas. Uso: python segments.py voz.mp3"""
import re, subprocess, sys
p = sys.argv[1]
out = subprocess.run(["ffmpeg", "-i", p, "-af", "silencedetect=noise=-32dB:d=0.15", "-f", "null", "-"], capture_output=True, text=True).stderr
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p], capture_output=True, text=True).stdout)
ss = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", out)]; se = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", out)]
segs, cur = [], 0.0
for a, b in zip(ss, se):
    if a > cur + 0.05: segs.append((cur, a))
    cur = b
if cur < dur - 0.05: segs.append((cur, dur))
for i, (a, b) in enumerate(segs): print(f"{i:2d}  {a:6.2f} → {b:6.2f}")
print(f"duración total: {dur:.2f}")
