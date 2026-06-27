import Sidebar from "./Sidebar";

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex bg-zinc-950 text-white">
      <Sidebar />

      <div className="flex-1">
        {children}
      </div>
    </div>
  );
}