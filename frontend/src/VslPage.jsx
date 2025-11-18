import React, { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import VslExpandedView from "./components/VslExpandedView";

function VslPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const vsl = location.state?.vsl;

  const [snackbarOpen, setSnackbarOpen] = useState(false);

  const handleCopyTranscript = async () => {
    if (!vsl?.transcript_full) return;
    try {
      await navigator.clipboard.writeText(vsl.transcript_full);
      setSnackbarOpen(true);
      setTimeout(() => setSnackbarOpen(false), 4000);
    } catch (err) {
      console.error("Failed to copy transcript:", err);
    }
  };

  if (!vsl) {
    return (
      <div
        style={{
          minHeight: "100vh",
          background: "#000",
          color: "white",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          padding: "16px",
          textAlign: "center",
        }}
      >
        <p>No VSL data found for this page.</p>
        <button
          onClick={() => navigate("/")}
          style={{
            marginTop: "12px",
            padding: "10px 18px",
            borderRadius: "8px",
            border: "1px solid #444",
            background: "#111",
            color: "white",
            cursor: "pointer",
          }}
        >
          Go back to Swipe
        </button>
      </div>
    );
  }

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#000",
      }}
    >
      <header
        style={{
          padding: "12px 16px",
          borderBottom: "1px solid #222",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
        }}
      >
        <button
          onClick={() => navigate(-1)}
          style={{
            padding: "8px 14px",
            borderRadius: "8px",
            border: "1px solid #444",
            background: "#111",
            color: "white",
            cursor: "pointer",
          }}
        >
          ← Back
        </button>
        <h1
          style={{
            color: "white",
            fontSize: "1.1rem",
            margin: 0,
            textAlign: "center",
            flex: 1,
          }}
        >
          VSL Details
        </h1>
        <div style={{ width: "90px" }} /> {/* espaçador */}
      </header>

      <main
        style={{
          maxWidth: "960px",
          margin: "0 auto",
          padding: "16px",
        }}
      >
        {/* Botão Download VSL acima do container do vídeo */}
        <div
          style={{
            display: "flex",
            justifyContent: "flex-end",
            marginBottom: "12px",
          }}
        >
          <a
            href={vsl.video_path}
            download
            style={{
              padding: "8px 16px",
              borderRadius: "8px",
              border: "1px solid #444",
              background: "#1a1a1a",
              color: "white",
              textDecoration: "none",
              fontSize: "0.9rem",
            }}
          >
            Download VSL
          </a>
        </div>

        <VslExpandedView
          title={vsl.title}
          videoPath={vsl.video_path}
          transcript={vsl.transcript_full}
          onCopyTranscript={handleCopyTranscript}
        />
      </main>

      {snackbarOpen && (
        <div
          style={{
            position: "fixed",
            bottom: "30px",
            left: "50%",
            transform: "translateX(-50%)",
            background: "#333",
            color: "white",
            padding: "14px 24px",
            borderRadius: "8px",
            fontSize: "1rem",
            boxShadow: "0 4px 18px rgba(0,0,0,0.4)",
            zIndex: 9999,
          }}
        >
          transcription copied
        </div>
      )}
    </div>
  );
}

export default VslPage;
