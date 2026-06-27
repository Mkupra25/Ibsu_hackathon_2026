import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2 } from 'lucide-react';

interface ChatProps {
  onDataReceived: (data: any, chartInfo: any) => void;
}

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  isError?: boolean;
}

export function Chat({ onDataReceived }: ChatProps) {
  const [messages, setMessages] = useState<Message[]>([
    { id: '1', text: 'გამარჯობა! რით შემიძლია დაგეხმაროთ მონაცემების ანალიზში?', sender: 'bot' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { id: Date.now().toString(), text: userMessage, sender: 'user' }]);
    setIsLoading(true);

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: userMessage })
      });

      if (!response.ok) {
        throw new Error('API შეცდომა');
      }

      const data = await response.json();
      
      setMessages(prev => [...prev, { id: Date.now().toString(), text: data.answer, sender: 'bot' }]);
      
      if (data.data || data.chart) {
        onDataReceived(data.data, data.chart);
      }
    } catch (error) {
      setMessages(prev => [...prev, { 
        id: Date.now().toString(), 
        text: 'ბოდიშით, სერვერთან კავშირისას მოხდა შეცდომა.', 
        sender: 'bot',
        isError: true 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <Bot size={24} className="bot-icon" />
        <h2>AI ასისტენტი</h2>
      </div>
      
      <div className="messages-list">
        {messages.map(msg => (
          <div key={msg.id} className={`message-wrapper ${msg.sender}`}>
            <div className={`message-avatar ${msg.sender}`}>
              {msg.sender === 'bot' ? <Bot size={18} /> : <User size={18} />}
            </div>
            <div className={`message-bubble ${msg.sender} ${msg.isError ? 'error' : ''}`}>
              <p>{msg.text}</p>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="message-wrapper bot">
            <div className="message-avatar bot">
              <Bot size={18} />
            </div>
            <div className="message-bubble bot loading">
              <Loader2 className="spinner" size={18} />
              <span>ფიქრობს...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-area">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          placeholder="კითხეთ მონაცემებზე..."
          disabled={isLoading}
        />
        <button onClick={handleSend} disabled={isLoading || !input.trim()}>
          <Send size={20} />
        </button>
      </div>
    </div>
  );
}
