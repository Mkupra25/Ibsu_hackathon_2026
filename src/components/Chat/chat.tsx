import { useState, useEffect, useRef } from "react";

type Message = { role: "user" | "ai"; text: string };

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");

  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: Message = { role: "user", text: input };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");

    const aiResponse = await getAIResponse(input);

    const aiMessage: Message = { role: "ai", text: aiResponse };

    setMessages((prev) => [...prev, aiMessage]);
  };

  const getAIResponse = async (text: string) => {
    return "თქვენ დაწერეთ: " + text;
  };

  // auto scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="chat-wrapper">
      <div className="chat-box">

        {/* messages */}
        <div className="chat-messages">
          {messages.length === 0 && (
            <div className="empty-state">
              დაწერეთ პირველი შეტყობინება...
            </div>
          )}

          {messages.map((msg, i) => (
            <div
              key={i}
              className={`msg ${msg.role}`}
            >
              {msg.text}
            </div>
          ))}

          <div ref={messagesEndRef} />
        </div>

        {/* input */}
        <div className="chat-input">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="დაწერეთ შეტყობინება..."
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          />

          <button onClick={sendMessage}>
            გაგზავნა
          </button>
        </div>

      </div>
    </div>
  );
}