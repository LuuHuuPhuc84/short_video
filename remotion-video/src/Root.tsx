import { Composition } from "remotion";
import { MainVideo, MainVideoProps } from "./MainVideo";
import { BookVideoTNH, BookVideoProps } from "./BookVideoTNH";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {/* 1. Composition cho video thông thường (hỗ trợ cả BookVideoTNH) */}
      <Composition
        id="TiktokShort"
        component={BookVideoTNH}
        durationInFrames={1800}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{}}
        calculateMetadata={({ props }) => {
          const p = props as unknown as BookVideoProps;
          return {
            durationInFrames: Number(p?.durationInFrames) || 1800,
            fps: Number(p?.fps) || 30,
            width: Number(p?.width) || 1080,
            height: Number(p?.height) || 1920,
          };
        }}
      />

      {/* 2. Composition độc lập cho series Sách Thích Nhất Hạnh */}
      <Composition
        id="BookVideoTNH"
        component={BookVideoTNH}
        durationInFrames={1800}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{}}
        calculateMetadata={({ props }) => {
          const p = props as unknown as BookVideoProps;
          return {
            durationInFrames: Number(p?.durationInFrames) || 1800,
            fps: Number(p?.fps) || 30,
            width: Number(p?.width) || 1080,
            height: Number(p?.height) || 1920,
          };
        }}
      />
    </>
  );
};
