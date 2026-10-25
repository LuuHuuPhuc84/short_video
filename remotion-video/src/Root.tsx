import { Composition } from "remotion";
import { ZenShortVideo, ZenShortVideoProps } from "./ZenShortVideo";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {/* 1. Composition Shorts chuẩn cho kênh Nửa Chén Trà */}
      <Composition
        id="TiktokShort"
        component={ZenShortVideo}
        durationInFrames={1800}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{}}
        calculateMetadata={({ props }) => {
          const p = props as unknown as ZenShortVideoProps;
          return {
            durationInFrames: Number(p?.durationInFrames) || 1800,
            fps: Number(p?.fps) || 30,
            width: Number(p?.width) || 1080,
            height: Number(p?.height) || 1920,
          };
        }}
      />

      {/* 2. Composition ZenShortVideo */}
      <Composition
        id="ZenShortVideo"
        component={ZenShortVideo}
        durationInFrames={1800}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{}}
        calculateMetadata={({ props }) => {
          const p = props as unknown as ZenShortVideoProps;
          return {
            durationInFrames: Number(p?.durationInFrames) || 1800,
            fps: Number(p?.fps) || 30,
            width: Number(p?.width) || 1080,
            height: Number(p?.height) || 1920,
          };
        }}
      />

      {/* 3. Composition alias tương thích ngược */}
      <Composition
        id="BookVideoTNH"
        component={ZenShortVideo}
        durationInFrames={1800}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{}}
        calculateMetadata={({ props }) => {
          const p = props as unknown as ZenShortVideoProps;
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
