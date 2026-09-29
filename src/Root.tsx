import { Composition } from "remotion";
import { StickerLesson, TOTAL_FRAMES } from "./StickerLesson";

export const RemotionRoot: React.FC = () => (
  <Composition
    id="StickerLesson"
    component={StickerLesson}
    durationInFrames={TOTAL_FRAMES}
    fps={30}
    width={1080}
    height={1920}
  />
);
