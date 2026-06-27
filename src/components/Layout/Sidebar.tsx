import { NavLink } from "react-router-dom";
import { LayoutDashboard, MessageSquare, Package, Users, ShoppingCart } from "lucide-react";

import logo from "../../assets/logo.png";

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand" style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '32px', padding: '0 12px' }}>
        <img src={logo} alt="BeeEye Logo" style={{ width: '40px', height: '40px', borderRadius: '8px' }} />
        <h1 className="sidebar-title" style={{ margin: 0, padding: 0 }}>BeeEye</h1>
      </div>

      <div className="sidebar-section">
        <p className="sidebar-label">მთავარი</p>
        <nav className="sidebar-nav">
          <NavLink to="/" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}>
            <LayoutDashboard size={20} />
            დეშბორდი
          </NavLink>
        </nav>
      </div>

      <div className="sidebar-section">
        <p className="sidebar-label">AI ასისტენტი</p>
        <nav className="sidebar-nav">
          <NavLink to="/chat" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}>
            <MessageSquare size={20} />
            ჩათი
          </NavLink>
        </nav>
      </div>

      <div className="sidebar-section">
        <p className="sidebar-label">მონაცემთა ბაზა</p>
        <nav className="sidebar-nav">
          <NavLink to="/products" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}>
            <Package size={20} />
            პროდუქტები
          </NavLink>
          <NavLink to="/customers" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}>
            <Users size={20} />
            კლიენტები
          </NavLink>
          <NavLink to="/orders" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}>
            <ShoppingCart size={20} />
            შეკვეთები
          </NavLink>
        </nav>
      </div>
    </aside>
  );
}