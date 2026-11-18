"""Música de fondo sintetizada (sin copyright) + efectos (whoosh/pop) para el video."""
import sys, numpy as np, wave

SR = 44100
def save(path, x):
    x = np.clip(x, -1, 1)
    st = (np.stack([x[0], x[1]], 1) * 32767).astype(np.int16) if x.ndim == 2 else np.stack([x, x], 1).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(st.tobytes())

def lowpass(x, cutoff):
    # filtro de un polo, simple
    a = np.exp(-2 * np.pi * cutoff / SR); y = np.empty_like(x); s = 0.0
    for i in range(len(x)): s = (1 - a) * x[i] + a * s; y[i] = s
    return y

def note(f): return 440 * 2 ** ((f - 69) / 12)

def music(dur):
    n = int(dur * SR); t = np.arange(n) / SR
    L = np.zeros(n); R = np.zeros(n)
    bpm = 96; beat = 60 / bpm; bar = beat * 4
    chords = [[57, 60, 64, 69], [53, 57, 60, 65], [48, 52, 55, 60], [55, 59, 62, 67]]  # Am F C G
    # pad
    for k in range(int(dur / bar) + 1):
        ch = chords[k % 4]; s0 = int(k * bar * SR); s1 = min(n, int((k + 1) * bar * SR) + int(0.3 * SR))
        if s0 >= n: break
        tt = np.arange(s1 - s0) / SR
        env = np.minimum(1, tt / 0.6) * np.minimum(1, (s1 - s0) / SR - tt + 0.05)
        for j, m in enumerate(ch):
            f = note(m)
            v = (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(2 * np.pi * f * 2.003 * tt)) * env * 0.05
            L[s0:s1] += v * (0.7 if j % 2 else 1.0); R[s0:s1] += v * (1.0 if j % 2 else 0.7)
    # arpegio pluck (curiosidad)
    step = beat / 2
    for k in range(int(dur / step)):
        ch = chords[int(k * step / bar) % 4]
        m = ch[[0, 2, 1, 3, 2, 1, 3, 2][k % 8]] + 12
        s0 = int(k * step * SR); ln = int(0.5 * SR); s1 = min(n, s0 + ln)
        tt = np.arange(s1 - s0) / SR
        v = np.sin(2 * np.pi * note(m) * tt) * np.exp(-tt * 9) * 0.06
        pan = 0.5 + 0.35 * np.sin(k * 0.7)
        L[s0:s1] += v * (1 - pan); R[s0:s1] += v * pan
    # pulso grave suave + hi-hat ligero
    rng = np.random.default_rng(1)
    for k in range(int(dur / beat)):
        s0 = int(k * beat * SR); s1 = min(n, s0 + int(0.25 * SR)); tt = np.arange(s1 - s0) / SR
        kick = np.sin(2 * np.pi * (45 + 60 * np.exp(-tt * 30)) * tt) * np.exp(-tt * 14) * 0.22
        L[s0:s1] += kick; R[s0:s1] += kick
        h0 = int((k + 0.5) * beat * SR); h1 = min(n, h0 + int(0.05 * SR))
        if h0 < n:
            hh = rng.standard_normal(h1 - h0) * np.exp(-np.arange(h1 - h0) / SR * 80) * 0.025
            hh = hh - lowpass(hh, 6000)
            L[h0:h1] += hh; R[h0:h1] += hh
    fade = np.minimum(1, t / 0.8) * np.minimum(1, (dur - t) / 1.2)
    return np.stack([L * fade, R * fade])

def sfx(dur, whooshes, pops):
    n = int(dur * SR); L = np.zeros(n); R = np.zeros(n); rng = np.random.default_rng(3)
    for w in whooshes:  # ruido con barrido de filtro
        ln = int(0.45 * SR); s0 = max(0, int((w - 0.3) * SR)); s1 = min(n, s0 + ln)
        tt = np.arange(s1 - s0) / ln
        noise = rng.standard_normal(s1 - s0)
        env = np.sin(np.pi * tt) ** 2
        hi = lowpass(noise, 4000) - lowpass(noise, 300)
        v = hi * env * 0.25
        L[s0:s1] += v * (1 - tt); R[s0:s1] += v * tt
    for p in pops:  # "pop" con tono descendente + brillo
        s0 = int(p * SR); s1 = min(n, s0 + int(0.35 * SR)); tt = np.arange(s1 - s0) / SR
        v = np.sin(2 * np.pi * (900 * np.exp(-tt * 12) + 220) * tt) * np.exp(-tt * 10) * 0.3
        v += np.sin(2 * np.pi * 1760 * tt) * np.exp(-tt * 18) * 0.12
        L[s0:s1] += v; R[s0:s1] += v
    return np.stack([L, R])

if __name__ == "__main__":
    dur = float(sys.argv[1]); whooshes = [float(x) for x in sys.argv[2].split(",")]
    pops = [float(x) for x in sys.argv[3].split(",")]
    save("audio/music.wav", music(dur)); save("audio/sfx.wav", sfx(dur, whooshes, pops))
