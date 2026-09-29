"""Генерирует фоновую музыку и звуковые эффекты для ролика (без внешних сэмплов)."""
import wave
import numpy as np

SR = 44100
BPM = 120
BEAT = 60 / BPM
DUR = 31.0
rng = np.random.default_rng(7)


def write(path, x):
    x = np.clip(x, -1, 1)
    st = np.stack([x, x], 1) if x.ndim == 1 else x
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((st * 32767).astype("<i2").tobytes())


def env(n, a=0.005, d=0.2):
    t = np.arange(n) / SR
    return np.minimum(t / a, 1) * np.exp(-t / d)


def note(f, length, kind="pluck"):
    n = int(length * SR)
    t = np.arange(n) / SR
    if kind == "pluck":
        s = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(4 * np.pi * f * t) + 0.12 * np.sin(6 * np.pi * f * t)
        return s * env(n, 0.003, 0.18)
    if kind == "bass":
        s = np.tanh(2.2 * np.sin(2 * np.pi * f * t))
        return s * env(n, 0.004, 0.22)
    if kind == "pad":
        s = sum(np.sin(2 * np.pi * f * (1 + dt) * t) for dt in (-0.004, 0, 0.004)) / 3
        a = np.minimum(t / 0.3, 1) * np.minimum((length - t) / 0.3, 1)
        return s * a


def midi(m):
    return 440 * 2 ** ((m - 69) / 12)


N = int(DUR * SR)
mix = np.zeros(N)


def add(sig, at, gain=1.0):
    i = int(at * SR)
    j = min(N, i + len(sig))
    if i < N:
        mix[i:j] += sig[: j - i] * gain


# Аккорды: C - G - Am - F (по такту)
chords = [[60, 64, 67], [55, 59, 62], [57, 60, 64], [53, 57, 60]]
bar = 4 * BEAT
n_bars = int(DUR / bar) + 1

kick_n = int(0.35 * SR)
tk = np.arange(kick_n) / SR
kick = np.sin(2 * np.pi * (45 + 110 * np.exp(-tk * 30)) * tk) * np.exp(-tk * 9)
clap = rng.standard_normal(int(0.2 * SR))
clap = np.convolve(clap, np.ones(6) / 6, "same") * env(len(clap), 0.001, 0.06)
hat = np.diff(rng.standard_normal(int(0.06 * SR) + 1)) * env(int(0.06 * SR), 0.001, 0.015)

for b in range(n_bars):
    t0 = b * bar
    ch = chords[b % 4]
    intro = b == 0
    for k in range(4):
        if not intro or k >= 2:
            add(kick, t0 + k * BEAT, 0.9)
        if k in (1, 3) and not intro:
            add(clap, t0 + k * BEAT, 0.35)
    for k in range(8):
        add(hat, t0 + k * BEAT / 2 + BEAT / 4, 0.18)
        if not intro:
            add(note(midi(ch[0] - 24), BEAT / 2, "bass"), t0 + k * BEAT / 2, 0.32)
    for k in range(16):
        m = ch[[0, 1, 2, 1][k % 4]] + 12 * (1 if k % 8 >= 4 else 0) + 12
        add(note(midi(m), BEAT / 2, "pluck"), t0 + k * BEAT / 4, 0.16)
    for m in ch:
        add(note(midi(m), bar, "pad"), t0, 0.05)

# Плавное затухание в конце
fade = int(2.5 * SR)
mix[-fade:] *= np.linspace(1, 0, fade)
mix /= np.max(np.abs(mix)) / 0.85
write("public/music.wav", mix)

# «Поп» для появления стикера
n = int(0.18 * SR)
t = np.arange(n) / SR
pop = np.sin(2 * np.pi * (300 + 1400 * t / 0.18) * t) * env(n, 0.002, 0.05)
write("public/pop.wav", pop * 0.8)

# «Вжух» для перехода
n = int(0.45 * SR)
t = np.arange(n) / SR
noise = rng.standard_normal(n)
out = np.zeros(n)
state = 0.0
for i in range(n):
    a = 0.02 + 0.5 * np.sin(np.pi * t[i] / 0.45) ** 2
    state += a * (noise[i] - state)
    out[i] = state
out *= np.sin(np.pi * t / 0.45) ** 1.5
write("public/whoosh.wav", out / np.max(np.abs(out)) * 0.6)
print("ok")
