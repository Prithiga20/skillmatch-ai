import { useState, useRef, useEffect } from "react";
import api from "../api";

const SUGGESTIONS = [
  { label: "📄 Resume Tips",        msg: "resume tips" },
  { label: "🎯 Interview Advice",   msg: "interview tips" },
  { label: "💰 Salary Negotiation", msg: "salary negotiation" },
  { label: "🚀 Skill Development",  msg: "skill development" },
  { label: "🔍 Job Search",         msg: "job search tips" },
  { label: "📈 Career Growth",      msg: "career growth" },
  { label: "🎓 Fresher Tips",       msg: "fresher tips" },
  { label: "🤝 Networking",         msg: "networking tips" },
];

const GREETING = `👋 Hi! I'm your Career Guidance Assistant powered by SkillMatch AI.

I can help you with:
• 📄 Resume & Cover Letter Tips
• 🎯 Interview Preparation
• 💰 Salary Negotiation
• 🚀 Skill Development
• 🔍 Job Search Strategies
• 📈 Career Growth & Promotion
• 🎓 Fresher Advice
• 🤝 Networking Tips

What would you like help with today?`;

export default function Chatbot() {
  const [messages, setMessages] = useState([{ from: "bot", text: GREETING, time: now() }]);
  const [input, setInput]       = useState("");
  const [typing, setTyping]     = useState(false);
  const bottomRef = useRef(null);
  const inputRef  = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, typing]);

  const send = async (text) => {
    const msg = (text || input).trim();
    if (!msg) return;
    setInput("");
    setMessages(prev => [...prev, { from: "user", text: msg, time: now() }]);
    setTyping(true);
    try {
      const { data } = await api.post("/enhance/chatbot", { message: msg });
      // Simulate typing delay for natural feel
      await delay(600 + Math.random() * 400);
      setTyping(false);
      setMessages(prev => [...prev, { from: "bot", text: data.reply, time: now() }]);
    } catch {
      setTyping(false);
      setMessages(prev => [...prev, { from: "bot", text: "⚠️ Sorry, I couldn't process that. Please try again.", time: now() }]);
    }
    inputRef.current?.focus();
  };

  const clearChat = () => {
    setMessages([{ from: "bot", text: GREETING, time: now() }]);
  };

  return (
    <div className="chatbot-page">
      {/* Header */}
      <div className="chatbot-header">
        <div className="chatbot-avatar">🤖</div>
        <div>
          <h2>Career Guidance Assistant</h2>
          <span className="chatbot-status">● Online — ready to help</span>
        </div>
        <button className="btn-secondary" style={{ marginLeft: "auto" }} onClick={clearChat}>
          Clear Chat
        </button>
      </div>

      {/* Chat Window */}
      <div className="chat-window">
        {messages.map((m, i) => (
          <div key={i} className={`chat-row ${m.from}`}>
            {m.from === "bot" && <div className="chat-avatar-sm">🤖</div>}
            <div className={`chat-bubble ${m.from}`}>
              <FormattedText text={m.text} />
              <span className="chat-time">{m.time}</span>
            </div>
          </div>
        ))}

        {typing && (
          <div className="chat-row bot">
            <div className="chat-avatar-sm">🤖</div>
            <div className="chat-bubble bot typing-bubble">
              <span className="dot" /><span className="dot" /><span className="dot" />
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Suggestion Chips */}
      <div className="chat-suggestions">
        {SUGGESTIONS.map((s) => (
          <button key={s.msg} className="suggestion-chip" onClick={() => send(s.msg)}>
            {s.label}
          </button>
        ))}
      </div>

      {/* Input Bar */}
      <div className="chat-input-bar">
        <input
          ref={inputRef}
          type="text"
          placeholder="Ask me anything about your career..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
          disabled={typing}
        />
        <button
          className="btn-primary chat-send-btn"
          onClick={() => send()}
          disabled={typing || !input.trim()}
        >
          {typing ? "..." : "Send ➤"}
        </button>
      </div>
    </div>
  );
}

// Renders bullet points and line breaks properly
function FormattedText({ text }) {
  return (
    <div className="chat-text">
      {text.split("\n").map((line, i) => (
        <p key={i} style={{ margin: line === "" ? "0.3rem 0" : "0.1rem 0" }}>
          {line}
        </p>
      ))}
    </div>
  );
}

function now() {
  return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function delay(ms) {
  return new Promise(res => setTimeout(res, ms));
}
