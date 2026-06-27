import { type ReactNode } from "react";
import Sidebar from "./Sidebar";

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <div className="flex h-screen bg-black text-white">
      <Sidebar />

      <main className="flex-1 p-6 overflow-auto">
        {children}
      </main>
    </div>
  );
}