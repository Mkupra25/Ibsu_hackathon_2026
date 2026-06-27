import { NavLink } from "react-router-dom";

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <h1 className="text-xl font-bold mb-6">მენიუ</h1>

      <NavLink to="/" className="block p-2 rounded bg-gray-800 hover:bg-gray-700">
        მთავარი
      </NavLink>

      <div className="mt-6">
        <p className="text-gray-400 text-sm mb-2">AI აგენტი</p>
        <NavLink to="/chat" className="block p-2 rounded bg-gray-800 hover:bg-gray-700">
          ჩათი
        </NavLink>
      </div>

      <div className="mt-6">
        <p className="text-gray-400 text-sm mb-2">ბაზა</p>
        <NavLink to="/products" className="block p-2 rounded bg-gray-800 hover:bg-gray-700">
          პროდუქტები
        </NavLink>
        <NavLink to="/customers" className="block p-2 rounded bg-gray-800 hover:bg-gray-700">
          კლიენტები
        </NavLink>
        <NavLink to="/orders" className="block p-2 rounded bg-gray-800 hover:bg-gray-700">
          შეკვეთები
        </NavLink>
      </div>
    </aside>
  );
}