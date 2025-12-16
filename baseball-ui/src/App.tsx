import { useState } from "react";
import { postChat } from "./api";
import "./App.css";
import "./index.css";

type Msg = { role: "user" | "bot"; text: string };

export default function App() {
  const [msgs, setMsgs] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const send = async () => {
    const prompt = input.trim();
    if (!prompt || loading) return;
    setMsgs((m) => [...m, { role: "user", text: prompt }]);
    setInput("");
    setError(null);
    setLoading(true);
    try {
      const res = await postChat(prompt);
      setMsgs((m) => [...m, { role: "bot", text: res.message || "(no reply)" }]);
    } catch (e: any) {
      setError(e?.message || "Request failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <header>
        <div className="brand">Diamond Desk</div>
        <p>LLM + live MLB stats (Ollama + FastAPI)</p>
      </header>
      <main className="shell">
        <div className="chat">
          {msgs.map((m, i) => (
            <div key={i} className={`bubble ${m.role}`}>
              <strong>{m.role === "user" ? "You" : "Bot"}</strong>
              <p>{m.text}</p>
            </div>
          ))}
        </div>
        <div className="input-row">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && send()}
            placeholder="Ask about games, players, teams..."
          />
          <button onClick={send} disabled={loading}>
            {loading ? "..." : "Ask"}
          </button>
        </div>
        {error && <div className="error">{error}</div>}
      </main>
    </div>
  );
}
