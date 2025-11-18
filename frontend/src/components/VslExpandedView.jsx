// frontend/src/components/VslExpandedView.jsx
import React from "react";

function VslExpandedView({ title, videoPath, transcript, onCopyTranscript }) {
  const safeText = transcript || "";
  const displayedText = safeText ? `${safeText} [...]` : "";

  const handleCopyClick = () => {
    if (onCopyTranscript) {
      onCopyTranscript();
    }
  };

  return (
    <div
      style={{
        backgroundColor: "#111",
        padding: "24px",
        borderRadius: "16px",
        marginTop: "20px",
      }}
    >
      {/* Vídeo Player */}
      <video
        src={videoPath}
        controls
        style={{
          width: "100%",
          borderRadius: "12px",
          marginBottom: "20px",
          backgroundColor: "black",
        }}
      />

      {/* Título */}
      <h2
        style={{
          color: "white",
          fontSize: "1.6rem",
          marginBottom: "12px",
          wordBreak: "break-all",
        }}
      >
        {title}
      </h2>

      {/* Bloco da transcrição com botão Copy */}
      <div
        style={{
          position: "relative",
          backgroundColor: "#000",
          borderRadius: "12px",
          paddingTop: "40px", // espaço pro botão
          paddingBottom: "20px",
          paddingLeft: "20px",
          paddingRight: "20px",
          border: "1px solid #333",
          minHeight: "8em",
        }}
      >
        <button
          type="button"
          onClick={handleCopyClick}
          style={{
            position: "absolute",
            top: "10px",
            left: "10px",
            padding: "4px 10px",
            fontSize: "0.8rem",
            borderRadius: "999px",
            border: "1px solid #555",
            backgroundColor: "#222",
            color: "#f5f5f5",
            cursor: "pointer",
          }}
        >
          Copy
        </button>

        <pre
          style={{
            whiteSpace: "pre-wrap",
            color: "#d6d6d6",
            lineHeight: "1.6",
            fontSize: "1rem",
            margin: 0,
            display: "-webkit-box",
            WebkitLineClamp: 5,          // 🔥 limita visualmente a 5 linhas
            WebkitBoxOrient: "vertical", // necessário pro line-clamp
            overflow: "hidden",
          }}
        >
          {displayedText}
        </pre>
      </div>
    </div>
  );
}

export default VslExpandedView;
