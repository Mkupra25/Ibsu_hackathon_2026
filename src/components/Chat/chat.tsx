import { useState, type JSX } from "react";

type Message = { role: "user" | "ai"; text: string };

export default function Chat(): JSX.Element {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState<string>("");

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: Message = { role: "user", text: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");

    const aiResponse = await getAIResponse(input);
    const aiMessage: Message = { role: "ai", text: aiResponse };

    setMessages((prev) => [...prev, aiMessage]);
  };

  const getAIResponse = async (text: string): Promise<string> => {
    return "You said: " + text;
  };

  return (
    <div className="flex flex-col h-screen bg-black text-white p-4">
      <div className="flex-1 overflow-y-auto space-y-2">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={
              msg.role === "user"
                ? "text-right"
                : "text-left text-green-400"
            }
          >
            {msg.text}
          </div>
        ))}
      </div>

      {/* BIGGER CHAT BAR */}
      <div className="flex gap-3 mt-4 p-3 bg-gray-900 rounded-xl">
        <input
          className="flex-1 p-4 text-black rounded-lg text-lg outline-none"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type a message..."
        />

        <button
          onClick={sendMessage}
          className="bg-blue-500 px-6 py-4 rounded-lg text-lg font-semibold"
        >
          Send
        </button>
      </div>
    </div>
  );
}