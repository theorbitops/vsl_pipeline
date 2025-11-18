// frontend/src/components/AdminIngestPage.jsx
import React, { useState } from "react";
import { Link } from "react-router-dom";

const API_BASE = "http://localhost:8000";

function AdminIngestPage() {
  const [urlsText, setUrlsText] = useState("");
  const [bulkResult, setBulkResult] = useState(null);
  const [batchSize, setBatchSize] = useState("");
  const [ingestResult, setIngestResult] = useState(null);
  const [loadingBulk, setLoadingBulk] = useState(false);
  const [loadingIngest, setLoadingIngest] = useState(false);

  const handleSendUrls = async () => {
    const urls = urlsText
      .split("\n")
      .map((line) => line.trim())
      .filter((line) => line.length > 0);

    if (urls.length === 0) {
      alert("Paste at least one URL.");
      return;
    }

    setLoadingBulk(true);
    setBulkResult(null);

    try {
      const res = await fetch(`${API_BASE}/urls/bulk`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          source: "admin_paste",
          urls,
        }),
      });

      const data = await res.json();
      setBulkResult(JSON.stringify(data, null, 2));
    } catch (err) {
      setBulkResult("Error sending URLs: " + String(err));
    } finally {
      setLoadingBulk(false);
    }
  };

  const handleRunIngest = async () => {
    const payload = {};

    if (batchSize.trim()) {
      const n = parseInt(batchSize, 10);
      if (Number.isNaN(n) || n <= 0) {
        alert("batch_size must be a positive integer.");
        return;
      }
      payload.batch_size = n;
    }

    setLoadingIngest(true);
    setIngestResult(null);

    try {
      const res = await fetch(`${API_BASE}/admin/run_ingest_now`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await res.json();
      setIngestResult(JSON.stringify(data, null, 2));
    } catch (err) {
      setIngestResult("Error running ingest: " + String(err));
    } finally {
      setLoadingIngest(false);
    }
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#050505",
        color: "#f5f5f5",
      }}
    >
      <header
        style={{
          borderBottom: "1px solid #181818",
          padding: "16px 0",
        }}
      >
        <div
          style={{
            maxWidth: "1120px",
            margin: "0 auto",
            padding: "0 16px",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            gap: "12px",
          }}
        >
          <div>
            <h1
              style={{
                margin: 0,
                fontSize: "1.5rem",
                fontWeight: 600,
              }}
            >
              VSL Ingestion
            </h1>
            <p
              style={{
                margin: "4px 0 0",
                fontSize: "0.9rem",
                color: "#a0a0a0",
              }}
            >
              
            </p>
          </div>

          {/* Botão para voltar pro Swipe */}
          <Link
            to="/"
            style={{
              padding: "8px 14px",
              borderRadius: "8px",
              border: "1px solid #333",
              background: "#111",
              color: "#f5f5f5",
              fontSize: "0.85rem",
              textDecoration: "none",
              whiteSpace: "nowrap",
            }}
          >
            ← Back to Swipe
          </Link>
        </div>
      </header>

      <main
        style={{
          maxWidth: "1120px",
          margin: "0 auto",
          padding: "16px",
          paddingBottom: "32px",
        }}
      >
        {/* Block 1: /urls/bulk */}
        <section
          style={{
            background: "#0f0f0f",
            borderRadius: "16px",
            border: "1px solid #222",
            padding: "18px",
            boxShadow: "0 18px 50px rgba(0,0,0,0.4)",
          }}
        >
          <h2
            style={{
              marginTop: 0,
              marginBottom: "8px",
              fontSize: "1.1rem",
            }}
          >
            1. Submit URLs for ingestion
          </h2>
          <p
            style={{
              marginTop: 0,
              marginBottom: "10px",
              fontSize: "0.9rem",
              color: "#b0b0b0",
            }}
          >
            1 VSL (m3u8) per line:
          </p>

          <textarea
            value={urlsText}
            onChange={(e) => setUrlsText(e.target.value)}
            rows={8}
            placeholder={`https://cdn.../main.m3u8\nhttps://cdn.../main.m3u8\n...`}
            style={{
              width: "100%",
              boxSizing: "border-box",
              fontFamily: "monospace",
              padding: "12px",
              borderRadius: "8px",
              background: "#111",
              color: "#f5f5f5",
              border: "1px solid #333",
              resize: "vertical",
            }}
          />

          <button
            onClick={handleSendUrls}
            disabled={loadingBulk}
            style={{
              marginTop: "10px",
              padding: "10px 18px",
              borderRadius: "8px",
              border: "1px solid #333",
              background: "#202020",
              color: "white",
              cursor: "pointer",
              fontSize: "0.95rem",
            }}
          >
            {loadingBulk ? "Sending URLs..." : "Submit URLs"}
          </button>

          <div style={{ marginTop: "14px" }}>
            <h3
              style={{
                margin: 0,
                marginBottom: "6px",
                fontSize: "0.95rem",
              }}
            >
              /urls/bulk response
            </h3>
            <pre
              style={{
                background: "#000",
                color: "#0f0",
                padding: "12px",
                borderRadius: "8px",
                maxHeight: "260px",
                overflow: "auto",
                fontSize: "0.8rem",
                boxSizing: "border-box",
              }}
            >
              {bulkResult || "No response yet."}
            </pre>
          </div>
        </section>

        {/* Block 2: /admin/run_ingest_now */}
        <section
          style={{
            marginTop: "24px",
            background: "#0f0f0f",
            borderRadius: "16px",
            border: "1px solid #222",
            padding: "18px",
            boxShadow: "0 18px 50px rgba(0,0,0,0.4)",
          }}
        >
          <h2
            style={{
              marginTop: 0,
              marginBottom: "8px",
              fontSize: "1.1rem",
            }}
          >
            2. Run ingest of pending URLs now
          </h2>
          <p
            style={{
              marginTop: 0,
              marginBottom: "10px",
              fontSize: "0.9rem",
              color: "#b0b0b0",
            }}
          >
            Optional: set a <code>batch_size</code> for this run (default is
            50).
          </p>

          <div
            style={{
              display: "flex",
              flexWrap: "wrap",
              gap: "8px",
              alignItems: "center",
              marginBottom: "8px",
            }}
          >
            <input
              type="number"
              min={1}
              value={batchSize}
              onChange={(e) => setBatchSize(e.target.value)}
              placeholder="e.g. 200"
              style={{
                padding: "8px",
                borderRadius: "8px",
                border: "1px solid #333",
                background: "#111",
                color: "#f5f5f5",
                width: "140px",
                boxSizing: "border-box",
              }}
            />

            <button
              onClick={handleRunIngest}
              disabled={loadingIngest}
              style={{
                padding: "10px 18px",
                borderRadius: "8px",
                border: "1px solid #333",
                background: "#202020",
                color: "white",
                cursor: "pointer",
                fontSize: "0.95rem",
              }}
            >
              {loadingIngest ? "Running ingest..." : "Run ingest now"}
            </button>
          </div>

          <div style={{ marginTop: "10px" }}>
            <h3
              style={{
                margin: 0,
                marginBottom: "6px",
                fontSize: "0.95rem",
              }}
            >
              /admin/run_ingest_now response
            </h3>
            <pre
              style={{
                background: "#000",
                color: "#0f0",
                padding: "12px",
                borderRadius: "8px",
                maxHeight: "220px",
                overflow: "auto",
                fontSize: "0.8rem",
                boxSizing: "border-box",
              }}
            >
              {ingestResult || "No response yet."}
            </pre>
          </div>
        </section>
      </main>
    </div>
  );
}

export default AdminIngestPage;
