# Нейроджимми · Занятие 3 — ролик про стикерпаки

Вертикальный ролик (1080×1920, ~30 с) о третьем занятии базового курса, на котором ребята создают свои стикерпаки.
Стикерпак: https://t.me/addstickers/Captainsmile111

## Сборка

1. Положите исходное видео занятия в `public/lesson.mp4`.
2. `npm install`
3. `python3 scripts/make_audio.py` — сгенерирует музыку и звуки в `public/` (нужен `numpy`).
4. `npm run studio` — предпросмотр, `npm run render` — рендер в `out/sticker-lesson.mp4`.

Сцены, подписи и тайминги задаются массивом `CLIPS` в `src/StickerLesson.tsx`.
Стикеры в `public/stickers/` вырезаны с экранов мониторов из видео занятия.
