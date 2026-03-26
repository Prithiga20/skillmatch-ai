import { useState, useRef, useEffect } from "react";
import api from "../api";

export default function Chatbot() {
  const [messages, setMessages] = useState([
    { from: "bot", text: "Hi! I'm your career assistant. Ask me about resumes, interviews, salary, skills, or job search tips!" }
  ]);
  const [input, setInput] = useState("");
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = async () => {
    if (!input.trim()) return;
    const userMsg = { from: "user", text: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    try {
      const { data } = await api.post("/enhance/chatbot", { message: input });
      setMessages((prev) => [...prev, { from: "bot", text: data.reply }]);
    } catch {
      setMessages((prev) => [...prev, { from: "bot", text: "Sorry, I couldn't process that. Try again." }]);
    }
  };

  const handleKey = (e) => {
    if (e.key === "Enter") send();
  };

  return (
    <div className="dashboard">
      <h2>Career Guidance Chatbot</h2>
      <div className="dashboard-section">
        <div className="chat-window">
          {messages.map((m, i) => (
            <div key={i} className={`chat-bubble ${m.from}`}>
              <span>{m.text}</span>
            </div>
          ))}
          <div ref={bottomRef} />
        </div>
        <div className="chat-input">
          <input
            type="text"
            placeholder="Ask about resume, interview, salary, skills..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKey}
          />
          <button className="btn-primary" onClick={send}>Send</button>
        </div>
        <div className="chat-suggestions">
          {["Resume tips", "Interview advice", "Salary negotiation", "Job search", "Career guidance"].map((s) => (
            <button key={s} className="btn-secondary" onClick={() => { setInput(s); }}>
              {s}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
