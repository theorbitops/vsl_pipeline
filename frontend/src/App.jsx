import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import SwipePage from "./SwipePage";
import VslPage from "./VslPage";
import AdminIngestPage from "./components/AdminIngestPage";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<SwipePage />} />
        <Route path="/vsl/:id" element={<VslPage />} />
        <Route path="/admin" element={<AdminIngestPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
