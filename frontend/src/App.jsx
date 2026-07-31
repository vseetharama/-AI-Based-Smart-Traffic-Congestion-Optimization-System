import { BrowserRouter, Routes, Route } from "react-router-dom";

import Home from "./pages/Home";
import Members from "./pages/Members";
import Dashboard from "./pages/Dashboard";
import Analytics from "./pages/Analytics";
import Upload from "./pages/Upload";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/members" element={<Members />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/upload" element={<Upload />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;