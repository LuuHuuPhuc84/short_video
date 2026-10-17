import React from "react";
import {
  AbsoluteFill,
  Audio,
  Img,
  Sequence,
  staticFile,
  useCurrentFrame,
  interpolate,
} from "remotion";
// Fallback rỗng nếu không có props
const defaultVideoData = {
  scenes: [],
  episode: 1,
  title: "TÂM CÀNG NÓNG VỘI, VIỆC CÀNG KHÓ THÀNH",
  audioFile: "voiceover.wav",
  durationInFrames: 300,
};

export interface SceneItem {
  scene: number;
  tag?: string;
  text: string;
  highlight: string;
  image: string;
  startFrame: number;
  durationInFrames: number;
}

export interface MainVideoProps {
  episode?: number;
  title?: string;
  subtitle?: string;
  fps?: number;
  width?: number;
  height?: number;
  durationInFrames?: number;
  audioFile?: string;
  scenes?: SceneItem[];
}

export const MainVideo: React.FC<MainVideoProps> = (props) => {
  const data = props && props.scenes && props.scenes.length > 0 ? props : (defaultVideoData as MainVideoProps);
  const episode = data.episode || 1;
  const title = data.title || "TÂM CÀNG NÓNG VỘI, VIỆC CÀNG KHÓ THÀNH";
  const audioFile = data.audioFile || "voiceover.wav";
  const scenes = data.scenes || [];
  const durationInFrames = data.durationInFrames || 300;

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#030712",
        fontFamily: "'Montserrat', 'SF Pro Display', 'Segoe UI', -apple-system, sans-serif",
        color: "#ffffff",
        overflow: "hidden",
      }}
    >
      {/* 1. Dynamic 6 B-roll Scenes với hiệu ứng Ken Burns luân phiên */}
      {scenes.map((scene: SceneItem, index: number) => (
        <Sequence
          key={`bg-${scene.scene}`}
          from={scene.startFrame}
          durationInFrames={scene.durationInFrames}
        >
          <SceneBackground
            imageSrc={staticFile(scene.image || `scene${index + 1}.jpg`)}
            durationInFrames={scene.durationInFrames}
            index={index}
          />
        </Sequence>
      ))}

      {/* 2. Cinematic Lighting Gradient nhẹ (Đảm bảo video sáng rõ, trong trẻo, không bị tối) */}
      <CinematicGradientOverlay />

      {/* 3. Audio (Giọng đọc + Nhạc nền Piano Thiền) */}
      <Audio src={staticFile(audioFile)} volume={1.0} />
      <Audio src={staticFile("background_music.mp3")} volume={0.12} />

      {/* 4. HERO HEADER: Xuất hiện 100% rõ nét ngay từ frame 0 (Thumbnail TikTok chuẩn) -> 80 frames (~2.6s) rồi fade out */}
      <Sequence from={0} durationInFrames={80}>
        <HeroHeader episode={episode} title={title} />
      </Sequence>

      {/* 5. Cụm chữ phụ đề Lower-Third: Tối ưu nhịp đọc theo từng câu ngắn (Không chứa tag kỹ thuật) */}
      {scenes.map((scene: SceneItem) => (
        <Sequence
          key={`text-${scene.scene}`}
          from={scene.startFrame}
          durationInFrames={scene.durationInFrames}
        >
          <PacedCaptionCard scene={scene} />
        </Sequence>
      ))}

      {/* 6. Neon Progress Bar */}
      <ProgressBar totalFrames={durationInFrames} />
    </AbsoluteFill>
  );
};

// Component Hero Header: Vị trí chuẩn TikTok Cover Safe Zone (top: 360px), hiển thị 100% ngay frame 0
const HeroHeader: React.FC<{ episode: number; title: string }> = ({
  episode,
  title,
}) => {
  const frame = useCurrentFrame();

  // Đảm bảo từ Frame 0 (ảnh thumbnail TikTok) đã hiển thị 100% rõ nét
  // Fade out và trượt nhẹ biến mất từ frame 58 đến 80 (~ sau 2.0 - 2.6 giây)
  const fadeOut = interpolate(frame, [58, 80], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const exitTranslateY = interpolate(frame, [58, 80], [0, -30], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <div
      style={{
        position: "absolute",
        top: 360, // Tọa độ vàng hiển thị trọn vẹn trong lưới ảnh bìa TikTok Profile (khung 3:4)
        left: 50,
        right: 50,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        zIndex: 30,
        transform: `translateY(${exitTranslateY}px)`,
        opacity: fadeOut,
      }}
    >
      {/* 1. SỐ THỨ TỰ: Chỉ ghi '#4' nhỏ gọn, sắc sảo và nổi bật */}
      <div
        style={{
          display: "inline-block",
          fontSize: 26,
          letterSpacing: 2,
          fontWeight: 900,
          color: "#030712",
          backgroundColor: "#fbbf24",
          padding: "6px 24px",
          borderRadius: 30,
          boxShadow: "0 6px 25px rgba(251, 191, 36, 0.6)",
          marginBottom: 16,
        }}
      >
        #{episode}
      </div>

      {/* 2. XUỐNG DÒNG -> KHUNG TIÊU ĐỀ CHÍNH: Chữ to (52px), tương phản cao, cuốn hút click */}
      <div
        style={{
          backgroundColor: "rgba(3, 7, 18, 0.88)",
          border: "2px solid rgba(251, 191, 36, 0.4)",
          borderRadius: 24,
          padding: "24px 36px",
          backdropFilter: "blur(20px)",
          boxShadow: "0 20px 50px rgba(0,0,0,0.85), 0 0 40px rgba(251, 191, 36, 0.2)",
          textAlign: "center",
          width: "100%",
          maxWidth: 980,
        }}
      >
        <h1
          style={{
            margin: 0,
            fontSize: 52,
            fontWeight: 900,
            lineHeight: 1.25,
            letterSpacing: 1.2,
            textTransform: "uppercase",
            color: "#ffffff",
            textShadow:
              "0 4px 14px rgba(0, 0, 0, 0.9), 0 0 25px rgba(251, 191, 36, 0.4)",
            display: "inline-block",
          }}
        >
          {title.split(",").map((part, i, arr) => (
            <React.Fragment key={i}>
              <span
                style={{
                  color: i % 2 === 0 ? "#f8fafc" : "#fbbf24",
                }}
              >
                {part.trim()}
              </span>
              {i < arr.length - 1 && <span style={{ color: "#fbbf24" }}>, </span>}
            </React.Fragment>
          ))}
        </h1>
      </div>
    </div>
  );
};

// Background Ken Burns luân phiên hướng chuyển động (Zoom in / Zoom out)
const SceneBackground: React.FC<{
  imageSrc: string;
  durationInFrames: number;
  index: number;
}> = ({ imageSrc, durationInFrames, index }) => {
  const frame = useCurrentFrame();

  const isEven = index % 2 === 0;
  const scale = isEven
    ? interpolate(frame, [0, durationInFrames], [1.0, 1.14])
    : interpolate(frame, [0, durationInFrames], [1.14, 1.0]);

  const translateY = interpolate(frame, [0, durationInFrames], [0, isEven ? -20 : 15]);

  return (
    <AbsoluteFill style={{ overflow: "hidden" }}>
      <Img
        src={imageSrc}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          transform: `scale(${scale}) translateY(${translateY}px)`,
        }}
      />
    </AbsoluteFill>
  );
};

// QUY CHUẨN MỚI (BẢO TOÀN ÁNH SÁNG GỐC 100%):
// Bỏ toàn bộ lớp phủ đen/gradient dìm tối toàn màn hình.
// Chỉ duy nhất ô hộp phụ đề (PacedCaptionCard) ở phía dưới là có nền kính mờ riêng để bảo đảm tương phản chữ.
const CinematicGradientOverlay: React.FC = () => {
  return null;
};

// Hiển thị cụm chữ phụ đề nhịp nhàng (Đã loại bỏ hoàn toàn các tag kỹ thuật)
const PacedCaptionCard: React.FC<{ scene: SceneItem }> = ({ scene }) => {
  return (
    <div
      style={{
        position: "absolute",
        bottom: 270, // Vùng an toàn chuẩn tránh caption & profile TikTok
        left: 50,
        right: 50,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        textAlign: "center",
        zIndex: 20,
      }}
    >
      {/* Thẻ phụ đề Glassmorphism */}
      <div
        style={{
          backgroundColor: "rgba(10, 15, 30, 0.85)",
          borderRadius: 26,
          padding: "32px 38px",
          border: "1px solid rgba(255, 255, 255, 0.16)",
          backdropFilter: "blur(24px)",
          boxShadow:
            "0 24px 60px rgba(0,0,0,0.75), inset 0 1px 0 rgba(255,255,255,0.25)",
          maxWidth: 980,
          width: "100%",
        }}
      >
        {/* Highlight Focus Headline */}
        {scene.highlight && (
          <div
            style={{
              fontSize: 38,
              fontWeight: 900,
              color: "#fbbf24",
              lineHeight: 1.3,
              marginBottom: 16,
              letterSpacing: 1.5,
              textShadow: "0 4px 20px rgba(251, 191, 36, 0.45)",
            }}
          >
            “ {scene.highlight} ”
          </div>
        )}

        {/* Lời thoại giọng đọc */}
        <div
          style={{
            fontSize: 35,
            fontWeight: 500,
            lineHeight: 1.55,
            color: "#f8fafc",
            textShadow: "0 2px 10px rgba(0,0,0,0.85)",
          }}
        >
          {scene.text}
        </div>
      </div>
    </div>
  );
};

const ProgressBar: React.FC<{ totalFrames: number }> = ({ totalFrames }) => {
  const frame = useCurrentFrame();
  const progress = Math.min((frame / totalFrames) * 100, 100);

  return (
    <div
      style={{
        position: "absolute",
        bottom: 0,
        left: 0,
        width: "100%",
        height: 7,
        backgroundColor: "rgba(255, 255, 255, 0.12)",
        zIndex: 30,
      }}
    >
      <div
        style={{
          width: `${progress}%`,
          height: "100%",
          backgroundColor: "#38bdf8",
          boxShadow: "0 0 12px #38bdf8",
        }}
      />
    </div>
  );
};
