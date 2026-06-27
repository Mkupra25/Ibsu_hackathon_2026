import { useState } from "react";

type Message = { role: "user" | "ai"; text: string };

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");

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

  return (
    <div className="chat-wrapper">
      {/* messages */}
      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="empty-state">დაწერეთ პირველი შეტყობინება...</div>
        )}

        {messages.map((msg, i) => (
          <div
            key={i}
            className={msg.role === "user" ? "msg user" : "msg ai"}
          >
            {msg.text}
          </div>
        ))}
      </div>

      {/* input */}
      <div className="chat-input">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="დაწერეთ შეტყობინება..."
        />

        <button onClick={sendMessage}>გაგზავნა</button>
      </div>
    </div>
  );
}