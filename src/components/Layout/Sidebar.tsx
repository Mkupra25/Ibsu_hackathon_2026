import { LayoutDashboard, TrendingUp, Shield, Bot, Settings } from "lucide-react";

export default function Sidebar(): import("react").JSX.Element {
  return (
    <div className="h-screen w-64 bg-zinc-950 border-r border-zinc-800 text-white p-4">
      
      <h1 className="text-xl font-bold mb-8">
        AI BI Dashboard
      </h1>

      <nav className="space-y-4 text-sm">

        <div className="flex items-center gap-3 hover:bg-zinc-900 p-2 rounded">
          <LayoutDashboard size={18} />
          Dashboard
        </div>
      </nav>

    </div>
  );
}