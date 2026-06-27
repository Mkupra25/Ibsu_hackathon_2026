import { useState, useEffect, useRef } from "react";
import axios from "axios";
import { useDashboard } from "../../context/DashboardContext";
import { Send, BotMessageSquare, Sparkles } from "lucide-react";
import "./chat.css";

export default function Chat() {
  const { messages, setMessages, conversationId, setConversationId, setDashboardData } = useDashboard();
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = { role: "user" as const, text: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await axios.post(`${API_URL}/api/chat`, {
        message: userMessage.text,
        // Pass conversation_id so the backend recalls past messages
        conversation_id: conversationId,
      });

      const { answer, chart, data, sql_query, conversation_id } = response.data;

      // Save the conversation_id returned by the backend for future requests
      if (conversation_id) {
        setConversationId(conversation_id);
      }

      const aiMessage = { role: "ai" as const, text: answer, sql: sql_query };
      setMessages((prev) => [...prev, aiMessage]);

      if (chart || data) {
        setDashboardData(chart || null, data || null, sql_query || null);
      }
    } catch (error) {
      const errorMessage = {
        role: "error" as const,
        text: "ბოდიშით, სერვერთან კავშირისას მოხდა შეცდომა. გთხოვ სცადე თავიდან.",
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  return (
    <div className="chat-wrapper">
      <div className="chat-box">

        {/* messages */}
        <div className="chat-messages">
          {messages.length === 0 && (
            <div className="empty-state">
              <BotMessageSquare size={52} />
              <p style={{ fontWeight: 600, fontSize: "1.2rem", color: "var(--text-main)" }}>
                გამარჯობა! მე ვარ BeeEye AI
              </p>
              <p style={{ color: "var(--text-muted)", maxWidth: "420px", lineHeight: 1.7 }}>
                დამისვი ნებისმიერი კითხვა ბიზნეს-მონაცემების შესახებ. <br />
                <strong style={{ color: "var(--primary)" }}>მაგ:</strong> &quot;ტოპ 5 პროდუქტი გაყიდვებით&quot; ან &quot;შემოსავალი ქალაქების მიხედვით&quot;
              </p>
              <div className="example-pills">
                {["ჯამური შემოსავალი?", "ტოპ 5 პროდუქტი", "შემოსავალი ქალაქების მიხედვით"].map((q) => (
                  <button
                    key={q}
                    className="pill-btn"
                    onClick={() => { setInput(q); }}
                  >
                    <Sparkles size={13} />
                    {q}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((msg, i) => (
            <div key={i} className={`msg ${msg.role === "error" ? "ai error" : msg.role}`}>
              {msg.role === "ai" && (
                <div className="ai-icon">
                  <BotMessageSquare size={16} />
                </div>
              )}
              <div className="msg-content">
                <span>{msg.text}</span>
                {msg.sql && (
                  <details className="sql-details">
                    <summary>🔍 SQL</summary>
                    <pre><code>{msg.sql}</code></pre>
                  </details>
                )}
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="msg ai">
              <div className="ai-icon">
                <BotMessageSquare size={16} />
              </div>
              <div className="typing-indicator">
                <span></span><span></span><span></span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* fixed input */}
        <div className="chat-input-container">
          <div className="chat-input">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="დასვი ბიზნეს კითხვა ქართულად..."
              onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && sendMessage()}
              disabled={isLoading}
            />
            <button onClick={sendMessage} disabled={isLoading || !input.trim()}>
              <Send size={18} />
            </button>
          </div>
          {conversationId && (
            <p className="session-hint">სესია აქტიურია · AI ახსოვს საუბარი</p>
          )}
        </div>

      </div>
    </div>
  );
}