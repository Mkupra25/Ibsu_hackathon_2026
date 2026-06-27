import Sidebar from "./components/Layout/Sidebar";
import { Routes, Route } from "react-router-dom";
import Dashboard from "./components/Dashboard/dashboard";
import Chat from "./components/Chat/chat";

export default function App() {
  return (
    <div className="app-layout">
      <Sidebar />

      <main className="main-content">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/chat" element={<Chat />} />
        </Routes>
      </main>
    </div>
  );
}