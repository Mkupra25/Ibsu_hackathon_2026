import Sidebar from "./components/Layout/Sidebar";
import { Routes, Route } from "react-router-dom";
import Dashboard from "./components/Dashboard/dashboard";
import Chat from "./components/Chat/chat";

export default function App() {
  return (
    <div className="layout">
      <div className="sidebar">
        <Sidebar />
      </div>

      <div className="content">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/chat" element={<Chat />} />
        </Routes>
      </div>
    </div>
  );
}