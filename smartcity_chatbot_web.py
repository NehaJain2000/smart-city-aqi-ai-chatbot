#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import webbrowser
import threading
import time
from groq import Groq

# ── APNI GROQ API KEY YAHAN PASTE KARO ─────────────
API_KEY = "Put you API Key"
# ───────────────────────────────────────────────────

client = Groq(api_key=API_KEY)

SYSTEM_PROMPT = """You are an AI assistant for a SmartCity Air Quality Dashboard project built in Power BI.
You help users understand air quality data for Indian cities.

AQI levels (India CPCB standards):
- 0-50: Good
- 51-100: Satisfactory
- 101-200: Moderate
- 201-300: Poor
- 301-400: Very Poor
- 401-500: Severe

You can answer questions about AQI levels, health impacts, city comparisons, PM2.5, NO2, O3 pollutants.
Keep answers concise and helpful. Always respond in English only."""

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SmartCity AI Chatbot</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  :root {
    --bg: #0f1117; --surface: #1a1d27; --surface2: #222535;
    --border: #2a2d3e; --accent: #4ade80; --accent2: #22d3ee;
    --text: #e8eaf0; --text-dim: #6b7280; --user-bg: #1e3a2f;
  }
  body { font-family: 'DM Sans', sans-serif; background: var(--bg); color: var(--text); height: 100vh; display: flex; flex-direction: column; overflow: hidden; }
  .header { padding: 16px 24px; border-bottom: 1px solid var(--border); display: flex; align-items: center; gap: 14px; background: var(--surface); }
  .header-dot { width: 10px; height: 10px; border-radius: 50%; background: var(--accent); box-shadow: 0 0 10px var(--accent); animation: pulse 2s infinite; }
  @keyframes pulse { 0%,100%{opacity:1;transform:scale(1)}50%{opacity:.6;transform:scale(.9)} }
  .header-text h1 { font-family: 'DM Serif Display', serif; font-size: 18px; color: var(--text); }
  .header-text p { font-size: 11px; color: var(--text-dim); margin-top: 1px; letter-spacing: .05em; text-transform: uppercase; }
  .header-badge { margin-left: auto; background: linear-gradient(135deg,#4ade8022,#22d3ee22); border: 1px solid #4ade8044; color: var(--accent); font-size: 10px; padding: 4px 10px; border-radius: 20px; letter-spacing: .1em; text-transform: uppercase; }
  .chat-area { flex: 1; overflow-y: auto; padding: 24px; display: flex; flex-direction: column; gap: 16px; scrollbar-width: thin; scrollbar-color: var(--border) transparent; }
  .welcome { text-align: center; padding: 40px 20px; animation: fadeIn .6s ease forwards; }
  @keyframes fadeIn { from{opacity:0} to{opacity:1} }
  .welcome-icon { font-size: 40px; margin-bottom: 16px; }

  /* Crossfade greeting */
  .greeting-wrapper {
    position: relative;
    height: 52px;
    margin-bottom: 6px;
  }
  .greeting-text {
    font-family: 'DM Serif Display', serif;
    font-size: 26px;
    color: var(--text);
    position: absolute;
    width: 100%;
    text-align: center;
    top: 0; left: 0;
    opacity: 0;
    transition: opacity 0.8s ease;
  }
  .greeting-text.visible { opacity: 1; }

  .lang-label {
    font-size: 13px;
    color: var(--accent);
    margin-bottom: 14px;
    height: 20px;
    letter-spacing: 0.08em;
    transition: opacity 0.4s ease;
  }

  .welcome p { font-size: 14px; color: var(--text-dim); line-height: 1.6; max-width: 400px; margin: 0 auto 24px; }
  .suggestions { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; }
  .suggestion { background: var(--surface2); border: 1px solid var(--border); color: var(--text-dim); font-size: 12px; padding: 8px 14px; border-radius: 20px; cursor: pointer; transition: all .2s; font-family: 'DM Sans', sans-serif; }
  .suggestion:hover { border-color: var(--accent); color: var(--accent); background: #4ade8011; }

  .message { display: flex; gap: 12px; opacity: 0; animation: slideIn .3s ease forwards; max-width: 85%; }
  @keyframes slideIn { from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:translateY(0)} }
  .message.user { margin-left: auto; flex-direction: row-reverse; }
  .message.bot { margin-right: auto; }
  .avatar { width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 14px; flex-shrink: 0; }
  .avatar.bot { background: linear-gradient(135deg,#4ade8033,#22d3ee33); border: 1px solid #4ade8044; }
  .avatar.user { background: var(--surface2); border: 1px solid var(--border); }
  .bubble { padding: 12px 16px; border-radius: 16px; font-size: 14px; line-height: 1.65; }
  .message.user .bubble { background: var(--user-bg); border: 1px solid #4ade8033; border-bottom-right-radius: 4px; color: #d1fae5; }
  .message.bot .bubble { background: var(--surface); border: 1px solid var(--border); border-bottom-left-radius: 4px; color: var(--text); }
  .typing .bubble { display: flex; gap: 4px; align-items: center; padding: 14px 18px; }
  .dot { width: 6px; height: 6px; border-radius: 50%; background: var(--accent); animation: bounce 1.2s infinite; }
  .dot:nth-child(2){animation-delay:.2s} .dot:nth-child(3){animation-delay:.4s}
  @keyframes bounce { 0%,60%,100%{transform:translateY(0);opacity:.4} 30%{transform:translateY(-6px);opacity:1} }
  .input-area { padding: 16px 24px; border-top: 1px solid var(--border); background: var(--surface); display: flex; gap: 12px; align-items: flex-end; }
  textarea { flex: 1; background: var(--surface2); border: 1px solid var(--border); border-radius: 12px; color: var(--text); font-family: 'DM Sans', sans-serif; font-size: 14px; padding: 12px 16px; resize: none; outline: none; min-height: 44px; max-height: 120px; transition: border-color .2s; line-height: 1.5; }
  textarea:focus { border-color: var(--accent); }
  textarea::placeholder { color: var(--text-dim); }
  .send-btn { width: 44px; height: 44px; background: linear-gradient(135deg,var(--accent),var(--accent2)); border: none; border-radius: 12px; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 18px; transition: all .2s; flex-shrink: 0; }
  .send-btn:hover { transform: scale(1.05); opacity: .9; }
  .send-btn:disabled { opacity: .4; cursor: not-allowed; transform: none; }
  .footer-note { text-align: center; font-size: 11px; color: var(--text-dim); padding: 8px; background: var(--surface); }
</style>
</head>
<body>

<div class="header">
  <div class="header-dot"></div>
  <div class="header-text">
    <h1>SmartCity AI Assistant</h1>
    <p>Air Quality Intelligence · Powered by Groq AI</p>
  </div>
  <div class="header-badge">● Live</div>
</div>

<div class="chat-area" id="chatArea">
  <div class="welcome" id="welcome">
    <div class="welcome-icon">🌍</div>
    <div class="greeting-wrapper" id="greetingWrapper"></div>
    <div class="lang-label" id="langLabel"></div>
    <p>Ask me anything about air quality, AQI levels, health advisories, and city pollution data.</p>
    <div class="suggestions">
      <button class="suggestion" onclick="sendSuggestion(this)">What should I do if Delhi AQI is 280?</button>
      <button class="suggestion" onclick="sendSuggestion(this)">What is PM2.5 and why is it dangerous?</button>
      <button class="suggestion" onclick="sendSuggestion(this)">Which city has the worst air quality?</button>
      <button class="suggestion" onclick="sendSuggestion(this)">Is AQI 150 safe to go outside?</button>
    </div>
  </div>
</div>

<div class="input-area">
  <textarea id="userInput" placeholder="Ask anything about air quality..." rows="1" onkeydown="handleKey(event)" oninput="autoResize(this)"></textarea>
  <button class="send-btn" id="sendBtn" onclick="sendMessage()">↑</button>
</div>
<div class="footer-note">SmartCity Dashboard · Data Analytics Project · Groq AI</div>

<script>
  const greetings = [
    { text: "Hello! I am SmartCity AI",        lang: "🇬🇧 English" },
    { text: "नमस्ते! मैं हूँ SmartCity AI",     lang: "🇮🇳 Hindi" },
    { text: "Hallo! Ich bin SmartCity AI",      lang: "🇩🇪 German" },
    { text: "Bonjour! Je suis SmartCity AI",    lang: "🇫🇷 French" },
    { text: "¡Hola! Soy SmartCity AI",          lang: "🇪🇸 Spanish" },
    { text: "こんにちは！SmartCity AIです",       lang: "🇯🇵 Japanese" },
    { text: "مرحباً! أنا SmartCity AI",         lang: "🇸🇦 Arabic" },
    { text: "Olá! Eu sou SmartCity AI",         lang: "🇧🇷 Portuguese" },
    { text: "Привет! Я SmartCity AI",           lang: "🇷🇺 Russian" },
    { text: "你好！我是 SmartCity AI",           lang: "🇨🇳 Chinese" },
  ];

  const wrapper = document.getElementById('greetingWrapper');
  const langLabel = document.getElementById('langLabel');
  let current = null;
  let idx = 0;

  function showNext() {
    const g = greetings[idx];

    // Fade out current
    if (current) {
      current.classList.remove('visible');
    }

    // Create new element
    const el = document.createElement('div');
    el.className = 'greeting-text';
    el.textContent = g.text;
    wrapper.appendChild(el);

    // Small delay then fade in — use same g object
    setTimeout(() => {
      el.classList.add('visible');
      langLabel.textContent = g.lang;
    }, 100);

    // Remove old after fade
    const old = current;
    setTimeout(() => { if (old) old.remove(); }, 900);

    current = el;
    idx = (idx + 1) % greetings.length;
  }

  showNext();
  setInterval(showNext, 3000);

  // Chat
  const chatArea = document.getElementById('chatArea');
  const userInput = document.getElementById('userInput');
  const sendBtn = document.getElementById('sendBtn');

  function autoResize(el) { el.style.height='auto'; el.style.height=Math.min(el.scrollHeight,120)+'px'; }
  function handleKey(e) { if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();sendMessage();} }
  function sendSuggestion(btn) { userInput.value=btn.textContent; sendMessage(); }

  function addMessage(text, role) {
    const welcome = document.getElementById('welcome');
    if (welcome) welcome.remove();
    const msg = document.createElement('div');
    msg.className = `message ${role}`;
    const avatar = document.createElement('div');
    avatar.className = `avatar ${role}`;
    avatar.textContent = role==='bot' ? '🌍' : '👤';
    const bubble = document.createElement('div');
    bubble.className = 'bubble';
    bubble.textContent = text;
    msg.appendChild(avatar);
    msg.appendChild(bubble);
    chatArea.appendChild(msg);
    chatArea.scrollTop = chatArea.scrollHeight;
  }

  function addTyping() {
    const msg = document.createElement('div');
    msg.className = 'message bot typing';
    msg.id = 'typing';
    msg.innerHTML = `<div class="avatar bot">🌍</div><div class="bubble"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div>`;
    chatArea.appendChild(msg);
    chatArea.scrollTop = chatArea.scrollHeight;
  }

  function removeTyping() { const t=document.getElementById('typing'); if(t) t.remove(); }

  async function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;
    addMessage(text, 'user');
    userInput.value=''; userInput.style.height='auto';
    sendBtn.disabled=true; addTyping();
    try {
      const res = await fetch('/chat', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({message:text})});
      const data = await res.json();
      removeTyping(); addMessage(data.reply, 'bot');
    } catch(e) { removeTyping(); addMessage('Something went wrong. Please try again.', 'bot'); }
    sendBtn.disabled=false; userInput.focus();
  }
</script>
</body>
</html>"""

conversation_history = []

class ChatHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args): pass
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(HTML_PAGE.encode('utf-8'))
    def do_POST(self):
        length = int(self.headers['Content-Length'])
        body = json.loads(self.rfile.read(length))
        user_msg = body.get('message', '')
        conversation_history.append({"role": "user", "content": user_msg})
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + conversation_history,
            max_tokens=300
        )
        reply = response.choices[0].message.content
        conversation_history.append({"role": "assistant", "content": reply})
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"reply": reply}).encode())

def open_browser():
    time.sleep(1)
    webbrowser.open("http://localhost:8765")

if __name__ == "__main__":
    print("="*45)
    print("  SmartCity AI Chatbot")
    print("="*45)
    print("  Browser mein khul raha hai...")
    print("  Band karne ke liye Ctrl+C dabaao")
    print("="*45)
    threading.Thread(target=open_browser, daemon=True).start()
    server = HTTPServer(('localhost', 8765), ChatHandler)
    server.serve_forever()