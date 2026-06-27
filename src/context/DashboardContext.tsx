import { createContext, useContext, useState, type ReactNode } from "react";

export type Message = {
  role: "user" | "ai" | "error";
  text: string;
  sql?: string;
};

export type ChartInfo = {
  chart_type: string;
  chart_title?: string;
  x_axis?: string;
  y_axis?: string;
} | null;

export type QueryResult = {
  columns: string[];
  rows: any[];
  row_count: number;
} | null;

export type Widget = {
  id: string;
  chartInfo: ChartInfo;
  queryResult: QueryResult;
  sqlQuery: string | null;
  timestamp: Date;
};

interface DashboardContextType {
  widgets: Widget[];
  setDashboardData: (chart: ChartInfo, data: QueryResult, sql: string | null) => void;
  clearWidgets: () => void;
  messages: Message[];
  setMessages: React.Dispatch<React.SetStateAction<Message[]>>;
  conversationId: string | null;
  setConversationId: (id: string | null) => void;
}

const DashboardContext = createContext<DashboardContextType | undefined>(undefined);

export function DashboardProvider({ children }: { children: ReactNode }) {
  const [widgets, setWidgets] = useState<Widget[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);

  const setDashboardData = (chart: ChartInfo, data: QueryResult, sql: string | null) => {
    if (!data || data.rows.length === 0) return;
    
    const newWidget: Widget = {
      id: Math.random().toString(36).substring(7),
      chartInfo: chart,
      queryResult: data,
      sqlQuery: sql,
      timestamp: new Date(),
    };
    
    // ახალი ვიჯეტი დაემატება სიის თავში
    setWidgets(prev => [newWidget, ...prev]);
  };

  const clearWidgets = () => {
    setWidgets([]);
  };

  return (
    <DashboardContext.Provider value={{ 
      widgets, setDashboardData, clearWidgets,
      messages, setMessages,
      conversationId, setConversationId
    }}>
      {children}
    </DashboardContext.Provider>
  );
}

export function useDashboard() {
  const context = useContext(DashboardContext);
  if (context === undefined) {
    throw new Error("useDashboard must be used within a DashboardProvider");
  }
  return context;
}
