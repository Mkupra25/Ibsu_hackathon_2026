import Sidebar from "./components/Layout/Sidebar";
import { Routes, Route } from "react-router-dom";
import Dashboard from "./components/Dashboard/dashboard";
import Chat from "./components/Chat/chat";
import { DashboardProvider } from "./context/DashboardContext";
import Customers from "./components/Info/customers";
import Products from "./components/Info/products";
import Orders from "./components/Info/orders";

export default function App() {
  return (
    <DashboardProvider>
      <div className="layout">
        <div className="sidebar-container">
          <Sidebar />
        </div>

        <div className="content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/chat" element={<Chat />} />
            <Route path="/customers" element={<Customers />} />
            <Route path="/products" element={<Products />} />
            <Route path="/orders" element={<Orders />} />
          </Routes>
        </div>
      </div>
    </DashboardProvider>
  );
}