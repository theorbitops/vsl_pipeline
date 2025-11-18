// frontend/src/components/VslCard.jsx
import React from "react";

function VslCard({ title, videoPath, snippet, onClick }) {
  return (
    <div
      onClick={onClick}
      style={{
        backgroundColor: "#111",
        padding: "18px",
        borderRadius: "16px",
        border: "1px solid #333",
        marginBottom: "20px",
        cursor: "pointer",
      }}
    >
      <video
        src={videoPath}
        controls={false}
        muted
        style={{
          width: "100%",
          borderRadius: "12px",
          marginBottom: "14px",
          backgroundColor: "black",
        }}
      />

      <h3
        style={{
          color: "white",
          fontSize: "1.2rem",
          marginBottom: "8px",
        }}
      >
        {title}
      </h3>

      <p
        style={{
          color: "#ccc",
          fontSize: "0.95rem",
          whiteSpace: "pre-wrap",
          lineHeight: "1.5",
        }}
      >
        {snippet}
      </p>
    </div>
  );
}

export default VslCard;
