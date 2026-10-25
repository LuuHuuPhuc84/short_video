import React from "react";
import {
  AbsoluteFill,
  Audio,
  Img,
  OffthreadVideo,
  Sequence,
  staticFile,
  useCurrentFrame,
  interpolate,
  Loop,
} from "remotion";

export interface SceneItem {
  scene: number;
  tag?: string;
  text: string;
  highlight: string;
  image: string;
  videoDurationInFrames?: number;
  startFrame: number;
  durationInFrames: number;
}

export interface BookVideoProps {
  id?: string;
  book?: string;
  author?: string;
  chapter?: string;
  title?: string;
  titleHook?: string;
  showTitleHook?: boolean;
  subtitle?: string;
  fps?: number;
  width?: number;
  height?: number;
  durationInFrames?: number;
  audioFile?: string;
  thumbnailImage?: string;
  showHeroHeader?: boolean;
  scenes?: SceneItem[];
}

export const BookVideoTNH: React.FC<BookVideoProps> = (props) => {
  const book = props.book || "AN TRÚ TRONG HIỆN TẠI";
  const author = props.author || "Thiền sư Thích Nhất Hạnh";
  const chapter = props.chapter || "CHƯƠNG 2: NGỒI THỞ VÀ KINH HÀNH";
  const title =
    props.title || "BÀI TẬP 60 GIÂY THỞ VÀ MỈM CƯỜI, GIẢI TỎA CĂNG THẲNG";
  const rawTitleHook =
    props.titleHook || props.scenes?.[0]?.highlight || title.split(",")[0] || "";
  const titleHook = rawTitleHook.trim();
  const shouldShowTitleHook =
    props.showTitleHook !== false && Boolean(titleHook);
  const audioFile = props.audioFile || "voiceover_ch2.wav";
  const thumbnailImage = props.thumbnailImage || "";
  const scenes = props.scenes || [];
  const durationInFrames = props.durationInFrames || 1800;

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#030712",
        fontFamily:
          "'Montserrat', 'SF Pro Display', 'Segoe UI', -apple-system, sans-serif",
        color: "#ffffff",
        overflow: "hidden",
      }}
    >
      {/* 0. THUMBNAIL COVER FRAME (FRAME 0 - 30, TỨC 1 GIÂY ĐẦU TIÊN):
          Bắt buộc hiển thị ảnh Thumbnail hoàn chỉnh 1080x1920 ở giây đầu tiên.
          Tối ưu 100% cho YouTube Shorts khi chọn ảnh bìa (chỉ cần kéo về frame 0).
          Sau 1s, cross-fade mượt mà sang video B-roll chuyển động. */}
      {thumbnailImage && (
        <Sequence from={0} durationInFrames={30}>
          <ThumbnailCoverFrame imageSrc={thumbnailImage} />
        </Sequence>
      )}

      {/* 1. Dynamic B-roll Scenes với hiệu ứng Ken Burns luân phiên & gối đầu chống chớp đen */}
      {scenes.map((scene: SceneItem, index: number) => {
        const nextScene = scenes[index + 1];
        // Kéo dài background vượt qua khoảng trống và gối đầu (overlap) 15 frame vào scene sau để cross-fade không bị đen
        const bgDuration = nextScene
          ? Math.max(
              scene.durationInFrames,
              nextScene.startFrame - scene.startFrame + 15
            )
          : Math.max(
              scene.durationInFrames,
              durationInFrames - scene.startFrame
            );

        return (
          <Sequence
            key={`bg-${scene.scene}`}
            from={scene.startFrame}
            durationInFrames={bgDuration}
          >
            <SceneBackground
              imageSrc={scene.image ? staticFile(scene.image) : ""}
              durationInFrames={bgDuration}
              index={index}
              videoDurationInFrames={scene.videoDurationInFrames}
            />
          </Sequence>
        );
      })}

      {/* 2. Cinematic Lighting Gradient nhẹ */}
      <CinematicGradientOverlay />

      {/* 3. Audio (Single Pre-mixed Voiceover + Piano BGM - Tránh crash Temp trên Windows) */}
      <Audio src={staticFile(audioFile)} volume={1.0} />

      {/* 4. Top persistent book & author badge xuyên suốt video */}
      <TopBookBadge book={book} author={author} />

      {/* 5. TITLE HOOK HEADER: 2-3s đầu (Frame 0-80) tối ưu làm Hook thị giác & Thumbnail YouTube Shorts */}
      {shouldShowTitleHook && (
        <Sequence from={0} durationInFrames={80}>
          <TitleHookHeader titleHook={titleHook} />
        </Sequence>
      )}

      {/* 6. Cụm chữ phụ đề Lower-Third */}
      {scenes.map((scene: SceneItem) => (
        <Sequence
          key={`text-${scene.scene}`}
          from={scene.startFrame}
          durationInFrames={scene.durationInFrames}
        >
          <PacedCaptionCard scene={scene} />
        </Sequence>
      ))}

      {/* 7. Thẻ Kênh CTA "Ngẫm Mỗi Ngày" (Phương án 1): Hiện ở 100 frames cuối (~3.3 giây) */}
      {durationInFrames > 120 && (
        <Sequence from={durationInFrames - 100} durationInFrames={100}>
          <EndChannelCard />
        </Sequence>
      )}

      {/* 8. Neon Progress Bar */}
      <ProgressBar totalFrames={durationInFrames} />
    </AbsoluteFill>
  );
};

// 0. Component ThumbnailCoverFrame: Khung hình 1s đầu (Frame 0–30) hiển thị 100% hình Thumbnail Shorts
const ThumbnailCoverFrame: React.FC<{ imageSrc: string }> = ({ imageSrc }) => {
  const frame = useCurrentFrame();
  // Giữ nguyên 100% từ frame 0 đến 24, cross-fade mượt mà trong 5 frames (25–29) sang video B-roll
  const opacity = interpolate(frame, [24, 29], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ zIndex: 60, opacity }}>
      <Img
        src={staticFile(imageSrc)}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
        }}
      />
    </AbsoluteFill>
  );
};

// Top Persistent Badge: Hiển thị thanh lịch tên sách và tác giả
const TopBookBadge: React.FC<{ book: string; author: string }> = ({
  book,
  author,
}) => {
  return (
    <div
      style={{
        position: "absolute",
        top: 130, // Vùng an toàn phía trên màn hình Shorts / TikTok
        left: 0,
        right: 0,
        display: "flex",
        justifyContent: "center",
        zIndex: 25,
        pointerEvents: "none",
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 10,
          backgroundColor: "rgba(3, 7, 18, 0.78)",
          border: "1px solid rgba(251, 191, 36, 0.35)",
          borderRadius: 30,
          padding: "8px 24px",
          backdropFilter: "blur(16px)",
          boxShadow: "0 6px 20px rgba(0, 0, 0, 0.5)",
        }}
      >
        <span style={{ fontSize: 20 }}>📖</span>
        <span
          style={{
            fontSize: 22,
            fontWeight: 800,
            letterSpacing: 1.5,
            color: "#fbbf24",
            textTransform: "uppercase",
          }}
        >
          {book}
        </span>
        <span style={{ color: "rgba(255, 255, 255, 0.4)", fontSize: 20 }}>•</span>
        <span
          style={{
            fontSize: 21,
            fontWeight: 700,
            letterSpacing: 0.8,
            color: "#f8fafc",
          }}
        >
          {author}
        </span>
      </div>
    </div>
  );
};

// Component TitleHookHeader: Tối ưu 1–2 giây đầu (Frame 0–55) làm Thumbnail tự động có CTR cao cho Shorts
const TitleHookHeader: React.FC<{
  titleHook: string;
}> = ({ titleHook }) => {
  const frame = useCurrentFrame();

  // Hiển thị rõ nét 100% từ frame 0 đến frame 65 (~2.2s), sau đó fade out mượt mà trong 15 frames tiếp theo (đến frame 80 ~ 2.67s)
  const fadeOut = interpolate(frame, [65, 80], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const exitTranslateY = interpolate(frame, [65, 80], [0, -30], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Chữ rất to, màu tương phản (trắng viền đen hoặc vàng), tối đa 6-8 chữ
  const fontSize = titleHook.length > 25 ? 54 : 64;

  return (
    <div
      style={{
        position: "absolute",
        top: 360, // Khoảng 1/3 trên màn hình, tránh che cạnh phải và đáy
        left: 60,
        right: 60,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        zIndex: 35,
        transform: `translateY(${exitTranslateY}px)`,
        opacity: fadeOut,
      }}
    >
      <div
        style={{
          backgroundColor: "rgba(10, 15, 30, 0.85)",
          border: "3px solid #fbbf24",
          borderRadius: 28,
          padding: "24px 38px",
          backdropFilter: "blur(24px)",
          boxShadow:
            "0 20px 50px rgba(0, 0, 0, 0.95), 0 0 40px rgba(251, 191, 36, 0.4)",
          textAlign: "center",
          maxWidth: 960,
          width: "100%",
        }}
      >
        <h1
          style={{
            margin: 0,
            fontSize,
            fontWeight: 900,
            lineHeight: 1.25,
            letterSpacing: 1.8,
            textTransform: "uppercase",
            color: "#fbbf24",
            textShadow:
              "0 4px 18px rgba(0, 0, 0, 1), 0 0 25px rgba(0, 0, 0, 0.9), 0 0 35px rgba(251, 191, 36, 0.6)",
            display: "inline-block",
            WebkitTextStroke: "1px rgba(0, 0, 0, 0.8)",
          }}
        >
          {titleHook}
        </h1>
      </div>
    </div>
  );
};

// Background Ken Burns & Video B-roll với slow-motion, loop chống đứng hình và chuyển cảnh cross-fade
const SceneBackground: React.FC<{
  imageSrc: string;
  durationInFrames: number;
  index: number;
  videoDurationInFrames?: number;
}> = ({ imageSrc, durationInFrames, index, videoDurationInFrames }) => {
  const frame = useCurrentFrame();

  if (!imageSrc) {
    return <AbsoluteFill style={{ backgroundColor: "#0a0f1e" }} />;
  }

  const isVideo =
    imageSrc.toLowerCase().endsWith(".mp4") ||
    imageSrc.toLowerCase().endsWith(".webm");

  const isEven = index % 2 === 0;
  const scale = isEven
    ? interpolate(frame, [0, durationInFrames], [1.0, 1.12], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      })
    : interpolate(frame, [0, durationInFrames], [1.12, 1.0], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });

  const translateY = interpolate(
    frame,
    [0, durationInFrames],
    [0, isEven ? -16 : 12],
    {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    }
  );

  // Hiệu ứng hòa tan (cross-fade) 12 frame đầu cho các cảnh tiếp nối, loại bỏ hoàn toàn hiện tượng chớp đen
  const fadeIn =
    index > 0
      ? interpolate(frame, [0, 12], [0, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        })
      : 1;

  // Tính toán tốc độ phát slow-motion (0.65x - 1.0x) để video kéo dài vừa khít câu thoại
  const origFrames = videoDurationInFrames || (index === 0 ? 150 : 240);
  const playbackRate = Math.min(
    1.0,
    Math.max(0.65, origFrames / durationInFrames)
  );
  const loopDuration = Math.max(30, Math.round(origFrames / playbackRate));

  return (
    <AbsoluteFill style={{ overflow: "hidden", opacity: fadeIn }}>
      {isVideo ? (
        <Loop durationInFrames={loopDuration}>
          <OffthreadVideo
            src={imageSrc}
            muted
            playbackRate={playbackRate}
            style={{
              width: "100%",
              height: "100%",
              objectFit: "cover",
              transform: `scale(${scale}) translateY(${translateY}px)`,
              filter: "contrast(1.02) saturate(0.92) sepia(0.08)",
            }}
          />
        </Loop>
      ) : (
        <Img
          src={imageSrc}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            transform: `scale(${scale}) translateY(${translateY}px)`,
            filter: "contrast(1.02) saturate(0.92) sepia(0.08)",
          }}
        />
      )}
    </AbsoluteFill>
  );
};

// QUY CHUẨN TÔNG MÀU "ZEN AMBER GLASS" & VIGNETTE THOANG THOẢNG:
// 1. Áp dụng ánh ấm hổ phách đồng nhất (4%)
// 2. Vignette cực nhẹ ngoài rìa (giữ 68% vùng trung tâm trong trẻo 100%, bảo vệ Badge & Subtitle)
const CinematicGradientOverlay: React.FC = () => {
  return (
    <AbsoluteFill style={{ pointerEvents: "none", zIndex: 5 }}>
      {/* Lớp phủ hổ phách ấm (Amber Wash) đồng nhất 4% */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          backgroundColor: "rgba(224, 169, 109, 0.04)",
          mixBlendMode: "color",
        }}
      />
      {/* Vignette cực nhẹ ở 4 góc ngoài rìa */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "radial-gradient(circle at 50% 50%, transparent 68%, rgba(0, 0, 0, 0.22) 100%)",
        }}
      />
    </AbsoluteFill>
  );
};

// Component hiển thị phụ đề với hiệu ứng nhảy nảy chữ từng từ (Word Bounce / Karaoke Pop) theo giọng đọc
const KaraokeWordBounce: React.FC<{
  text: string;
  durationInFrames: number;
}> = ({ text, durationInFrames }) => {
  const frame = useCurrentFrame();

  const words = React.useMemo(() => {
    const rawWords = text.trim().split(/\s+/);
    if (rawWords.length === 0) return [];

    // Phân bổ thời lượng theo độ dài từ và dấu câu
    const weights = rawWords.map((w) => {
      let weight = Math.max(w.length, 2);
      if (/[.,!?;:…]$/.test(w)) {
        weight += 3;
      }
      return weight;
    });

    const totalWeight = weights.reduce((acc, val) => acc + val, 0);

    let curr = 0;
    return rawWords.map((word, i) => {
      const dur = Math.max(
        3,
        Math.round((weights[i] / totalWeight) * durationInFrames)
      );
      const start = curr;
      const end = i === rawWords.length - 1 ? durationInFrames : curr + dur;
      curr = end;
      return { word, start, end };
    });
  }, [text, durationInFrames]);

  return (
    <div
      style={{
        fontSize: 38,
        lineHeight: 1.6,
        textAlign: "center",
        display: "flex",
        flexWrap: "wrap",
        justifyContent: "center",
        alignItems: "center",
        rowGap: 10,
        columnGap: 10,
      }}
    >
      {words.map((item, idx) => {
        const isCurrent = frame >= item.start && frame < item.end;
        const isPast = frame >= item.end;

        let scale = 1.0;
        let color = "rgba(255, 255, 255, 0.55)";
        let fontWeight = 600;
        let textShadow = "0 2px 8px rgba(0,0,0,0.85)";

        if (isCurrent) {
          const progress =
            (frame - item.start) / Math.max(item.end - item.start, 1);
          // Hiệu ứng nảy: giật to lên 1.25x rồi hạ về 1.14x
          scale = interpolate(progress, [0, 0.25, 1], [1.08, 1.25, 1.14], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          });
          color = "#fbbf24"; // Màu vàng kim rực rỡ
          fontWeight = 900;
          textShadow =
            "0 0 25px rgba(251, 191, 36, 0.95), 0 0 10px rgba(251, 191, 36, 0.7), 0 3px 10px rgba(0,0,0,0.95)";
        } else if (isPast) {
          color = "#ffffff";
          fontWeight = 700;
        }

        return (
          <span
            key={idx}
            style={{
              display: "inline-block",
              transform: `scale(${scale})`,
              transformOrigin: "center center",
              color,
              fontWeight,
              textShadow,
            }}
          >
            {item.word}
          </span>
        );
      })}
    </div>
  );
};

// Caption Card Lower-Third với Karaoke Word Bounce
const PacedCaptionCard: React.FC<{ scene: SceneItem }> = ({ scene }) => {
  return (
    <div
      style={{
        position: "absolute",
        bottom: 270, // Vùng an toàn chuẩn tránh caption TikTok
        left: 50,
        right: 50,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        textAlign: "center",
        zIndex: 20,
      }}
    >
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

        {/* Lời thoại giọng đọc nháy to từng từ theo nhịp đọc */}
        <KaraokeWordBounce
          text={scene.text}
          durationInFrames={scene.durationInFrames}
        />
      </div>
    </div>
  );
};

// Neon Progress Bar
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

// Component Thẻ Kênh CTA "Ngẫm Mỗi Ngày" (Phương án 1 - Hiện 3.3s cuối)
const EndChannelCard: React.FC = () => {
  const frame = useCurrentFrame();

  // Hiệu ứng trượt nhẹ từ dưới lên và mờ dần xuất hiện (trong 15 frames đầu)
  const translateY = interpolate(frame, [0, 18], [40, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const opacity = interpolate(frame, [0, 15], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const pulseScale = interpolate(
    Math.sin(frame * 0.15),
    [-1, 1],
    [0.97, 1.03]
  );

  return (
    <div
      style={{
        position: "absolute",
        top: 480, // Tọa độ trung tâm thị giác của video
        left: 60,
        right: 60,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        zIndex: 40,
        transform: `translateY(${translateY}px)`,
        opacity,
      }}
    >
      <div
        style={{
          backgroundColor: "rgba(3, 7, 18, 0.92)",
          border: "2px solid rgba(251, 191, 36, 0.7)",
          borderRadius: 32,
          padding: "36px 40px",
          backdropFilter: "blur(30px)",
          boxShadow:
            "0 25px 60px rgba(0, 0, 0, 0.9), 0 0 45px rgba(251, 191, 36, 0.35)",
          textAlign: "center",
          maxWidth: 960,
          width: "100%",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
        }}
      >
        {/* Biểu tượng Chén Trà thiền tinh tế */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            width: 76,
            height: 76,
            borderRadius: "50%",
            backgroundColor: "rgba(251, 191, 36, 0.15)",
            border: "1.5px solid #fbbf24",
            fontSize: 38,
            marginBottom: 16,
            boxShadow: "0 0 20px rgba(251, 191, 36, 0.4)",
          }}
        >
          🍵
        </div>

        {/* Tên Kênh TikTok */}
        <div
          style={{
            fontSize: 48,
            fontWeight: 900,
            letterSpacing: 2,
            color: "#fbbf24",
            textTransform: "uppercase",
            marginBottom: 12,
            textShadow:
              "0 4px 15px rgba(0, 0, 0, 0.9), 0 0 25px rgba(251, 191, 36, 0.5)",
          }}
        >
          NỬA CHÉN TRÀ
        </div>

        {/* Thông điệp định vị kênh */}
        <div
          style={{
            fontSize: 26,
            fontWeight: 600,
            color: "#e2e8f0",
            lineHeight: 1.45,
            marginBottom: 24,
            maxWidth: 780,
            letterSpacing: 0.5,
          }}
        >
          Nhìn sâu để sống nhẹ
        </div>

        {/* Nút bấm Kêu gọi Follow (hiệu ứng thở nhẹ) */}
        <div
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: 12,
            backgroundColor: "#fbbf24",
            color: "#030712",
            padding: "12px 36px",
            borderRadius: 40,
            fontSize: 26,
            fontWeight: 900,
            letterSpacing: 1.2,
            boxShadow: "0 8px 30px rgba(251, 191, 36, 0.7)",
            transform: `scale(${pulseScale})`,
          }}
        >
          <span>➕</span>
          <span>NHẤN THEO DÕI</span>
        </div>
      </div>
    </div>
  );
};
