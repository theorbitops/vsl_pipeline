import React, { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import VslCard from "./components/VslCard";
import { searchVsls } from "./lib/searchService";

function SwipePage() {
  const [searchTerm, setSearchTerm] = useState("");
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const navigate = useNavigate();

  const handleSearchChange = (event) => {
    const value = event.target.value;
    setSearchTerm(value);
  };

  useEffect(() => {
    const term = searchTerm.trim();

    if (term === "") {
      setResults([]);
      setErrorMessage("");
      setIsLoading(false);
      return;
    }

    let cancelled = false;

    const runSearch = async () => {
      setIsLoading(true);
      setErrorMessage("");

      try {
        const vsls = await searchVsls(term);

        if (!cancelled) {
          setResults(vsls);
        }
      } catch (err) {
        console.error(err);
        if (!cancelled) {
          setResults([]);
          setErrorMessage(
            "There was an error while searching. Please try again."
          );
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    };

    runSearch();

    return () => {
      cancelled = true;
    };
  }, [searchTerm]);

  const handleCardClick = (vsl) => {
    navigate(`/vsl/${vsl.id}`, { state: { vsl } });
  };

  return (
    <div className="swipe-root">
      {/* Top header */}
      <header className="swipe-header">
        <div className="swipe-header-inner">
          <div>
            <h1 className="swipe-title">Swipe</h1>
            <p className="swipe-subtitle"></p>
          </div>

          <div>
            <Link
              to="/admin"
              style={{
                padding: "8px 14px",
                borderRadius: "8px",
                border: "1px solid #333",
                background: "#111",
                color: "#f5f5f5",
                fontSize: "0.85rem",
                textDecoration: "none",
              }}
            >
              Admin
            </Link>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="swipe-main">
        {/* Search card */}
        <section className="swipe-search-card">
          <label htmlFor="search" className="swipe-search-label">
            Search transcript
          </label>
          <input
            id="search"
            type="text"
            className="swipe-search-input"
            value={searchTerm}
            onChange={handleSearchChange}
            style={{
              boxSizing: "border-box",
              width: "100%",
            }}
          />

          <p className="swipe-search-hint"></p>
        </section>

        {/* Results */}
        <section className="swipe-results-section">
          {searchTerm.trim() === "" && (
            <p className="swipe-results-hint">
              Start typing a keyword to see matching VSLs.
            </p>
          )}

          {searchTerm.trim() !== "" && isLoading && (
            <p className="swipe-results-hint">Searching VSLs…</p>
          )}

          {searchTerm.trim() !== "" && !isLoading && errorMessage && (
            <p className="swipe-results-hint">{errorMessage}</p>
          )}

          {searchTerm.trim() !== "" &&
            !isLoading &&
            !errorMessage &&
            results.length === 0 && (
              <p className="swipe-results-hint">
                No VSL found for{" "}
                <span className="swipe-results-term">“{searchTerm}”</span>. Try
                a different fragment.
              </p>
            )}

          {!isLoading && !errorMessage && results.length > 0 && (
            <div className="swipe-results-grid">
              {results.map((vsl) => (
                <VslCard
                  key={vsl.id}
                  title={vsl.title}
                  videoPath={vsl.video_path}
                  snippet={vsl.transcript_snippet}
                  onClick={() => handleCardClick(vsl)}
                />
              ))}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

export default SwipePage;
