import React from "react";
import {
  AbsoluteFill,
  Audio,
  Img,
  interpolate,
  OffthreadVideo,
  Sequence,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { loadFont } from "@remotion/fonts";

const TITLE = "Unbounded";
const BODY = "Nunito";
const CYR = "U+0301, U+0400-045F, U+0490-0491, U+04B0-04B1, U+2116";
const LAT = "U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD";
for (const [family, file] of [
  [TITLE, "unbounded"],
  [BODY, "nunito"],
] as const) {
  loadFont({ family, url: staticFile(`fonts/${file}-cyr.woff2`), weight: "200 1000", unicodeRange: CYR });
  loadFont({ family, url: staticFile(`fonts/${file}-lat.woff2`), weight: "200 1000", unicodeRange: LAT });
}

const FPS = 30;

const C = {
  violet: "#7b3cff",
  pink: "#ff4fa3",
  yellow: "#ffd23f",
  ink: "#1b1033",
  mint: "#3ee6c4",
};

type StickerName = "corgi" | "parrot" | "backpack" | "chill" | "smile";

type Clip = {
  from: number; // секунда исходного видео
  frames: number;
  tag?: string;
  title: string;
  sub?: string;
  sticker?: StickerName;
  stickerAt?: number;
  accent: string;
};

const CLIPS: Clip[] = [
  {
    from: 0,
    frames: 108,
    tag: "Нейроджимми · базовый курс",
    title: "Занятие 3",
    sub: "Создаём свой стикерпак!",
    accent: C.violet,
  },
  {
    from: 7.3,
    frames: 99,
    tag: "Шаг 1",
    title: "Придумываем героя",
    sub: "нейросеть рисует — мы командуем",
    sticker: "corgi",
    stickerAt: 30,
    accent: C.pink,
  },
  {
    from: 11.0,
    frames: 102,
    tag: "Шаг 2",
    title: "Убираем фон",
    sub: "стикер должен быть прозрачным ✨",
    sticker: "parrot",
    stickerAt: 36,
    accent: C.mint,
  },
  {
    from: 16.0,
    frames: 78,
    title: "Эмоции?",
    sub: "показываем сами 😜",
    sticker: "chill",
    stickerAt: 22,
    accent: C.yellow,
  },
  {
    from: 19.4,
    frames: 96,
    tag: "Шаг 3",
    title: "Собираем пак",
    sub: "каждый — со своим героем",
    sticker: "backpack",
    stickerAt: 30,
    accent: C.violet,
  },
  {
    from: 25.6,
    frames: 120,
    title: "Работа кипит!",
    sub: "и немного танцев 🕺",
    sticker: "smile",
    stickerAt: 34,
    accent: C.pink,
  },
  {
    from: 33.3,
    frames: 150,
    title: "Стикерпак готов!",
    sub: "🎉 🎉 🎉",
    accent: C.yellow,
  },
];

const END_FRAMES = 165;
const STARTS = CLIPS.reduce<number[]>(
  (acc, c, i) => [...acc, i === 0 ? 0 : acc[i - 1] + CLIPS[i - 1].frames],
  []
);
const END_START = STARTS[STARTS.length - 1] + CLIPS[CLIPS.length - 1].frames;
export const TOTAL_FRAMES = END_START + END_FRAMES;

// ---------- Общие элементы ----------

const Pill: React.FC<{ children: React.ReactNode; bg: string; color?: string; rotate?: number }> = ({
  children,
  bg,
  color = C.ink,
  rotate = 0,
}) => (
  <div
    style={{
      display: "inline-block",
      background: bg,
      color,
      padding: "14px 34px",
      borderRadius: 999,
      fontFamily: BODY,
      fontWeight: 900,
      fontSize: 40,
      letterSpacing: 1,
      textTransform: "uppercase",
      transform: `rotate(${rotate}deg)`,
      border: `6px solid ${C.ink}`,
      boxShadow: `8px 8px 0 ${C.ink}`,
    }}
  >
    {children}
  </div>
);

const Caption: React.FC<{ clip: Clip }> = ({ clip }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const pop = (delay: number) =>
    spring({ frame: frame - delay, fps, config: { damping: 11, stiffness: 160, mass: 0.7 } });
  const out = interpolate(frame, [clip.frames - 8, clip.frames], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const tagS = pop(2);
  const titleS = pop(6);
  const subS = pop(12);

  return (
    <AbsoluteFill
      style={{
        alignItems: "center",
        paddingTop: 150,
        opacity: out,
      }}
    >
      {clip.tag ? (
        <div style={{ transform: `scale(${tagS}) rotate(${-4 + 4 * (1 - tagS)}deg)`, marginBottom: 26 }}>
          <Pill bg={clip.accent} color={clip.accent === C.yellow || clip.accent === C.mint ? C.ink : "#fff"}>
            {clip.tag}
          </Pill>
        </div>
      ) : null}
      <div
        style={{
          fontFamily: TITLE,
          fontWeight: 800,
          fontSize: clip.title.length > 14 ? 84 : 104,
          lineHeight: 1.05,
          color: "#fff",
          textAlign: "center",
          padding: "0 50px",
          WebkitTextStroke: `14px ${C.ink}`,
          paintOrder: "stroke fill",
          textShadow: `0 10px 0 ${C.ink}`,
          transform: `scale(${titleS}) translateY(${(1 - titleS) * 60}px)`,
        }}
      >
        {clip.title}
      </div>
      {clip.sub ? (
        <div
          style={{
            marginTop: 30,
            transform: `scale(${subS}) rotate(2deg)`,
            background: "#fff",
            color: C.ink,
            fontFamily: BODY,
            fontWeight: 900,
            fontSize: 48,
            padding: "14px 34px",
            borderRadius: 26,
            border: `6px solid ${C.ink}`,
            boxShadow: `8px 8px 0 ${clip.accent}`,
          }}
        >
          {clip.sub}
        </div>
      ) : null}
    </AbsoluteFill>
  );
};

const Sticker: React.FC<{
  name: StickerName;
  size: number;
  rotate: number;
  delay?: number;
}> = ({ name, size, rotate, delay = 0 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame - delay;
  const s = spring({ frame: t, fps, config: { damping: 9, stiffness: 170, mass: 0.6 } });
  // лёгкое «парение» после появления
  const floatY = Math.sin(t / 14) * 8 * Math.min(1, Math.max(0, t / 20));
  const sway = Math.sin(t / 19) * 2.5;
  return (
    <div
      style={{
        width: size,
        height: size,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        transform: `translateY(${floatY + (1 - s) * 80}px) scale(${s}) rotate(${rotate + (1 - s) * -30 + sway}deg)`,
        opacity: t < 0 ? 0 : 1,
      }}
    >
      <Img
        src={staticFile(`stickers/${name}.png`)}
        style={{
          maxWidth: "100%",
          maxHeight: "100%",
          objectFit: "contain",
          filter: "drop-shadow(0 18px 22px rgba(20,8,48,0.45)) drop-shadow(0 3px 4px rgba(20,8,48,0.35))",
        }}
      />
    </div>
  );
};

const Flash: React.FC = () => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [0, 5], [0.7, 0], { extrapolateRight: "clamp" });
  return <AbsoluteFill style={{ background: "#fff", opacity: o }} />;
};

// ---------- Сцены ----------

const VideoClip: React.FC<{ clip: Clip; index: number }> = ({ clip, index }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const punch = spring({ frame, fps, config: { damping: 14, stiffness: 120 } });
  const drift = interpolate(frame, [0, clip.frames], [1.0, 1.08]);
  const scale = drift + (1 - punch) * 0.18;
  const shift = interpolate(frame, [0, clip.frames], [index % 2 ? -20 : 20, index % 2 ? 20 : -20]);

  return (
    <AbsoluteFill style={{ background: C.ink }}>
      <AbsoluteFill style={{ transform: `scale(${scale}) translateX(${shift}px)` }}>
        <OffthreadVideo
          src={staticFile("lesson.mp4")}
          startFrom={Math.round(clip.from * FPS)}
          volume={0.35}
          style={{ width: "100%", height: "100%", objectFit: "cover" }}
        />
      </AbsoluteFill>
      {/* затемнение сверху, чтобы подписи читались */}
      <AbsoluteFill
        style={{
          background: "linear-gradient(180deg, rgba(27,16,51,0.65) 0%, rgba(27,16,51,0) 38%)",
        }}
      />
      <Caption clip={clip} />
      {clip.sticker ? (
        <Sequence from={clip.stickerAt ?? 30} layout="none">
          <AbsoluteFill
            style={{
              justifyContent: "flex-end",
              alignItems: index % 2 ? "flex-end" : "flex-start",
              padding: "0 50px 230px 50px",
            }}
          >
            <Sticker name={clip.sticker} size={470} rotate={index % 2 ? 7 : -7} />
          </AbsoluteFill>
          <Audio src={staticFile("pop.wav")} volume={0.9} />
        </Sequence>
      ) : null}
      {index > 0 ? (
        <>
          <Flash />
          <Audio src={staticFile("whoosh.wav")} volume={0.35} />
        </>
      ) : null}
    </AbsoluteFill>
  );
};

const FINALE: { name: StickerName; x: number; y: number; size: number; rotate: number; at: number }[] = [
  { name: "corgi", x: 20, y: 760, size: 380, rotate: -10, at: 28 },
  { name: "chill", x: 660, y: 700, size: 390, rotate: 9, at: 38 },
  { name: "backpack", x: 60, y: 1220, size: 400, rotate: -5, at: 48 },
  { name: "parrot", x: 640, y: 1230, size: 380, rotate: 10, at: 58 },
  { name: "smile", x: 330, y: 960, size: 430, rotate: 2, at: 70 },
];

const FinaleStickers: React.FC = () => (
  <AbsoluteFill>
    {FINALE.map((st) => (
      <Sequence key={st.name} from={st.at} layout="none">
        <div style={{ position: "absolute", left: st.x, top: st.y }}>
          <Sticker name={st.name} size={st.size} rotate={st.rotate} />
        </div>
        <Audio src={staticFile("pop.wav")} volume={0.8} />
      </Sequence>
    ))}
  </AbsoluteFill>
);

const Confetti: React.FC = () => {
  const frame = useCurrentFrame();
  const colors = [C.violet, C.pink, C.yellow, C.mint, "#fff"];
  return (
    <AbsoluteFill style={{ overflow: "hidden" }}>
      {new Array(46).fill(0).map((_, i) => {
        const seed = (i * 9301 + 49297) % 233280;
        const x = (seed / 233280) * 1080;
        const speed = 7 + (i % 7) * 1.6;
        const y = ((frame * speed + i * 137) % 2200) - 200;
        const r = frame * (4 + (i % 5)) + i * 40;
        const w = 18 + (i % 4) * 6;
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: x + Math.sin((frame + i * 11) / 12) * 30,
              top: y,
              width: w,
              height: w * (i % 3 === 0 ? 1 : 0.45),
              borderRadius: i % 3 === 0 ? "50%" : 4,
              background: colors[i % colors.length],
              transform: `rotate(${r}deg)`,
              opacity: 0.9,
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};

const EndCard: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const pop = (d: number) => spring({ frame: frame - d, fps, config: { damping: 11, stiffness: 150 } });
  const bgShift = frame * 0.6;
  const fadeOut = interpolate(frame, [END_FRAMES - 12, END_FRAMES], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        background: `linear-gradient(${150 + bgShift / 4}deg, ${C.violet} 0%, #b43cff 45%, ${C.pink} 100%)`,
        alignItems: "center",
        justifyContent: "center",
        opacity: fadeOut,
      }}
    >
      {/* узор из точек */}
      <AbsoluteFill
        style={{
          backgroundImage: "radial-gradient(rgba(255,255,255,0.18) 3px, transparent 3px)",
          backgroundSize: "46px 46px",
          backgroundPosition: `${bgShift}px ${bgShift}px`,
        }}
      />
      <Confetti />
      <div style={{ transform: `scale(${pop(0)})` }}>
        <Pill bg={C.yellow} rotate={-3}>
          Нейроджимми · занятие 3
        </Pill>
      </div>
      <div
        style={{
          marginTop: 40,
          fontFamily: TITLE,
          fontWeight: 800,
          fontSize: 82,
          lineHeight: 1.08,
          color: "#fff",
          textAlign: "center",
          WebkitTextStroke: `12px ${C.ink}`,
          paintOrder: "stroke fill",
          textShadow: `0 9px 0 ${C.ink}`,
          transform: `scale(${pop(5)})`,
        }}
      >
        Вот наши
        <br />
        стикеры!
      </div>

      <div style={{ display: "flex", marginTop: 50, alignItems: "center" }}>
        <Sticker name="corgi" size={330} rotate={-9} delay={10} />
        <Sticker name="backpack" size={370} rotate={2} delay={14} />
        <Sticker name="parrot" size={330} rotate={8} delay={18} />
      </div>
      <div style={{ display: "flex", marginTop: -10, gap: 50, alignItems: "center" }}>
        <Sticker name="chill" size={380} rotate={-5} delay={22} />
        <Sticker name="smile" size={380} rotate={6} delay={26} />
      </div>

      <div
        style={{
          marginTop: 50,
          background: "#fff",
          color: C.ink,
          fontFamily: BODY,
          fontWeight: 900,
          fontSize: 50,
          padding: "26px 50px",
          borderRadius: 36,
          border: `7px solid ${C.ink}`,
          boxShadow: `12px 12px 0 ${C.ink}`,
          transform: `scale(${pop(32)}) rotate(-1.5deg)`,
        }}
      >
        До встречи на занятии! 👋
      </div>
    </AbsoluteFill>
  );
};

// ---------- Композиция ----------

export const StickerLesson: React.FC = () => {
  return (
    <AbsoluteFill style={{ background: C.ink }}>
      {CLIPS.map((clip, i) => (
        <Sequence key={i} from={STARTS[i]} durationInFrames={clip.frames}>
          <VideoClip clip={clip} index={i} />
          {i === CLIPS.length - 1 ? (
            <>
              <Confetti />
              <FinaleStickers />
            </>
          ) : null}
        </Sequence>
      ))}
      <Sequence from={END_START} durationInFrames={END_FRAMES}>
        <EndCard />
        <Flash />
        <Audio src={staticFile("whoosh.wav")} volume={0.35} />
      </Sequence>
      <Audio
        src={staticFile("music.wav")}
        volume={(f) => interpolate(f, [0, 15], [0, 0.5], { extrapolateRight: "clamp" })}
      />
    </AbsoluteFill>
  );
};
