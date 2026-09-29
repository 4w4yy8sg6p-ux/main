"""Фоновая музыка для ролика на записанных сэмплах живых инструментов.

Акустическая гитара, бас, глокеншпиль и маримба — FluidR3 GM
(https://github.com/gleitz/midi-js-soundfonts, CC BY 3.0),
ударные — acoustic-kit из https://github.com/Tonejs/audio.
Сэмплы скачиваются в .cache/samples при первом запуске.

Результат: public/music.wav (~31 с, 120 BPM, C–G–Am–F).
"""
import subprocess
import urllib.request
import wave
from pathlib import Path

import numpy as np
from scipy.signal import butter, fftconvolve, sosfilt

SR = 44100
BPM = 120
BEAT = 60 / BPM
BAR = 4 * BEAT
DUR = 31.0
CACHE = Path(".cache/samples")
FLUID = "https://raw.githubusercontent.com/gleitz/midi-js-soundfonts/gh-pages/FluidR3_GM"
KIT = "https://raw.githubusercontent.com/Tonejs/audio/master/drum-samples/acoustic-kit"
NAMES = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]
rng = np.random.default_rng(3)


# ---------- загрузка сэмплов ----------

def decode(path: Path) -> np.ndarray:
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
        check=True,
        capture_output=True,
    ).stdout
    return np.frombuffer(raw, dtype=np.float32).astype(np.float64)


_cache: dict[str, np.ndarray] = {}


def fetch(url: str, name: str) -> np.ndarray:
    if name not in _cache:
        path = CACHE / name
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            urllib.request.urlretrieve(url, path)
        _cache[name] = decode(path)
    return _cache[name]


def inst(instrument: str, midi: int) -> np.ndarray:
    note = f"{NAMES[midi % 12]}{midi // 12 - 1}"
    return fetch(f"{FLUID}/{instrument}-mp3/{note}.mp3", f"{instrument}/{note}.mp3")


def drum(piece: str) -> np.ndarray:
    return fetch(f"{KIT}/{piece}.mp3", f"kit/{piece}.mp3")


# ---------- микширование ----------

N = int(DUR * SR)
bus = {k: np.zeros((N, 2)) for k in ("gtr", "bass", "lead", "drums")}


def place(name, sig, at, gain=1.0, pan=0.0, length=None, human=0.008):
    """Кладёт сэмпл в шину; human — случайный сдвиг по времени (живая игра)."""
    at = at + rng.normal(0, human) if human else at
    if length is not None:
        n = min(len(sig), int(length * SR))
        sig = sig[:n].copy()
        rel = min(n, int(0.06 * SR))
        sig[n - rel :] *= np.linspace(1, 0, rel)
    i = max(0, int(at * SR))
    j = min(N, i + len(sig))
    if i >= N:
        return
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    bus[name][i:j, 0] += sig[: j - i] * gain * l
    bus[name][i:j, 1] += sig[: j - i] * gain * r


# Аккорды (гитарные голосовки, MIDI) и басовые ноты
CHORDS = [
    [48, 52, 55, 60, 64],  # C
    [43, 47, 50, 55, 59, 67],  # G
    [45, 52, 57, 60, 64],  # Am
    [41, 48, 53, 57, 60, 65],  # F
]
BASS = [36, 31, 33, 29]

# Мелодия глокеншпиля: (доля такта в восьмых, нота, длительность в восьмых)
HOOK = [
    [(0, 76, 1), (1, 79, 1), (2, 81, 1), (3, 79, 1), (4, 76, 2), (6, 74, 1), (7, 72, 1)],
    [(0, 74, 2), (2, 79, 2), (4, 71, 2), (6, 74, 2)],
    [(0, 72, 1), (1, 76, 1), (2, 81, 1), (3, 79, 1), (4, 76, 2), (6, 72, 2)],
    [(0, 77, 1), (1, 76, 1), (2, 72, 1), (3, 69, 1), (4, 72, 4)],
]
# Ответная фраза маримбы — пореже
ANSWER = [
    [(0, 67, 2), (3, 72, 1), (4, 76, 2), (6, 72, 2)],
    [(0, 71, 2), (3, 74, 1), (4, 79, 4)],
    [(0, 69, 2), (3, 72, 1), (4, 76, 2), (6, 72, 2)],
    [(0, 69, 2), (2, 72, 2), (4, 77, 4)],
]
E8 = BEAT / 2

# Гитарный бой: (восьмая, вниз/вверх, сила)
STRUM = [(0, "D", 1.0), (2, "D", 0.8), (3, "U", 0.55), (5, "U", 0.6), (6, "D", 0.85), (7, "U", 0.5)]

FINAL_BAR = 14  # на 28-й секунде — финальный аккорд


def strum(chord, at, direction, vel, until, pan, gain):
    notes = chord if direction == "D" else list(reversed(chord[-4:]))
    spread = 0.012 if direction == "D" else 0.008
    start = at + rng.normal(0, 0.006)
    for k, m in enumerate(notes):
        t = start + k * spread
        place("gtr", inst("acoustic_guitar_steel", m), t, gain * vel * rng.uniform(0.85, 1.0), pan,
              length=until - t, human=0)


for b in range(FINAL_BAR):
    t0 = b * BAR
    ch = CHORDS[b % 4]
    # две гитары (левая и правая) с немного разной игрой — «живая» ширина
    for pan, g in ((-0.45, 0.30), (0.45, 0.24)):
        for idx, (pos, d, v) in enumerate(STRUM):
            nxt = STRUM[idx + 1][0] if idx + 1 < len(STRUM) else 8
            strum(ch, t0 + pos * E8 + (0.012 if pan > 0 else 0), d, v, t0 + nxt * E8 + 0.05, pan, g)

    if b >= 1:
        root = BASS[b % 4]
        for pos, m, ln in [(0, root, 3), (3, root, 1), (4, root + 7, 2), (6, root + 12 if b % 2 else root, 2)]:
            place("bass", inst("electric_bass_finger", m), t0 + pos * E8, 0.9 * rng.uniform(0.85, 1), 0,
                  length=ln * E8 - 0.02)

    phrase = HOOK if b in range(2, 6) or b in range(8, 12) else ANSWER if b in (6, 7, 12, 13) else None
    if phrase:
        for pos, m, ln in phrase[b % 4]:
            instrument, g, pan = (("glockenspiel", 0.32, 0.3) if phrase is HOOK else ("marimba", 0.45, 0.2))
            place("lead", inst(instrument, m), t0 + pos * E8, g * rng.uniform(0.85, 1), pan,
                  length=ln * E8 + 0.35)

    # ударные
    full = b >= 1
    for k in range(8):
        accent = 0.55 if k % 2 == 0 else 0.35
        place("drums", drum("hihat"), t0 + k * E8, accent * rng.uniform(0.8, 1.05), 0.25)
    for pos in ([0, 3, 4] if full else [0, 4]):
        place("drums", drum("kick"), t0 + pos * E8, (1.0 if full else 0.7), 0)
    if full:
        for pos in (2, 6):
            place("drums", drum("snare"), t0 + pos * E8, 0.75 * rng.uniform(0.9, 1), -0.05)
    # сбивка томами перед сменой части
    if b in (1, 5, 11, 13):
        for k, piece in enumerate(["tom1", "tom1", "tom2", "tom3"]):
            place("drums", drum(piece), t0 + (6 + k * 0.5) * E8, 0.6, (-0.3 + k * 0.2))

# финальный аккорд: большой бой вниз, бас, бочка
tf = FINAL_BAR * BAR
for pan in (-0.45, 0.45):
    strum(CHORDS[0] + [67, 72], tf + (0.012 if pan > 0 else 0), "D", 1.0, DUR, pan, 0.32)
place("bass", inst("electric_bass_finger", 36), tf, 1.0, 0, length=2.5)
place("lead", inst("glockenspiel", 84), tf, 0.35, 0.3, length=2.5)
place("drums", drum("kick"), tf, 1.0, 0)
place("drums", drum("snare"), tf, 0.7, 0)

# ---------- сведение ----------

def reverb(x, seconds=1.4, decay=0.38):
    n = int(seconds * SR)
    t = np.arange(n) / SR
    ir = np.stack([rng.standard_normal(n), rng.standard_normal(n)], 1) * np.exp(-t / decay)[:, None]
    ir[: int(0.012 * SR)] = 0  # пред-задержка
    ir /= np.sqrt((ir**2).sum(0))
    return np.stack([fftconvolve(x[:, c], ir[:, c])[:N] for c in range(2)], 1)


def norm(x):
    return x / (np.max(np.abs(x)) + 1e-9)


def hp(x, hz):
    sos = butter(2, hz, "highpass", fs=SR, output="sos")
    return sosfilt(sos, x, axis=0)


def lp(x, hz):
    sos = butter(2, hz, "lowpass", fs=SR, output="sos")
    return sosfilt(sos, x, axis=0)


# эквализация: убираем «гул» гитар, бас держим в своём диапазоне
bus["gtr"] = hp(bus["gtr"], 140)
bus["lead"] = hp(bus["lead"], 300)
bus["bass"] = lp(hp(bus["bass"], 40), 2500)

mix = (
    norm(bus["gtr"]) * 0.60
    + norm(bus["bass"]) * 0.38
    + norm(bus["lead"]) * 0.42
    + norm(bus["drums"]) * 0.55
)
wet = reverb(norm(bus["gtr"]) * 0.55 + norm(bus["lead"]) * 0.42 + norm(bus["drums"]) * 0.2)
mix = mix + wet * 0.18

fade_in = int(0.05 * SR)
mix[:fade_in] *= np.linspace(0, 1, fade_in)[:, None]
fade = int(2.0 * SR)
mix[-fade:] *= np.linspace(1, 0, fade)[:, None]
mix = np.tanh(norm(mix) * 1.3) / np.tanh(1.3) * 0.9  # мягкий лимитер

with wave.open("public/music.wav", "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((np.clip(mix, -1, 1) * 32767).astype("<i2").tobytes())
print("ok, samples:", len(_cache))
