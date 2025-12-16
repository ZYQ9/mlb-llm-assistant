const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function postChat(prompt: string) {
  const res = await fetch(`${API}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt }),
  });

  if (!res.ok) {
    throw new Error(`Chat failed (${res.status})`);
  }

  return res.json() as Promise<{ message: string }>;
}
