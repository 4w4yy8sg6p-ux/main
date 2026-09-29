# Нейроджимми · Занятие 3 — ролик про стикерпаки

Вертикальный ролик (1080×1920, ~30 с) о третьем занятии базового курса, на котором ребята создают свои стикерпаки.
Стикерпак: https://t.me/addstickers/Captainsmile111

## Сборка

1. Положите исходное видео занятия в `public/lesson.mp4`.
2. `npm install`
3. `python3 scripts/make_audio.py` — звуки «поп» и «вжух», `python3 scripts/make_music.py` — фоновая музыка на сэмплах живых инструментов (нужны `numpy`, `scipy`, `ffmpeg`, доступ к GitHub).
4. `npm run studio` — предпросмотр, `npm run render` — рендер в `out/sticker-lesson.mp4`.

Сцены, подписи и тайминги задаются массивом `CLIPS` в `src/StickerLesson.tsx`.
Стикеры: исходники в `assets/stickers-src/`, прозрачные PNG с белой обводкой делает `python3 scripts/cutout_stickers.py` (нужны `numpy`, `scipy`, `pillow`).

## Музыка

Сэмплы инструментов: FluidR3 GM из [gleitz/midi-js-soundfonts](https://github.com/gleitz/midi-js-soundfonts) (CC BY 3.0),
ударные — acoustic-kit из [Tonejs/audio](https://github.com/Tonejs/audio).
