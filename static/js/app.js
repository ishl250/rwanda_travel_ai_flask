
async function sendMessage() {
  const input = document.getElementById('userInput');
  const text = input.value.trim();
  if (!text) return;
  addBubble(text, 'user');
  input.value = '';
  toggleSending(true);
  try {
    const res = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text })
    });
    const data = await res.json();
    if (data.ok) {
      addBubble(data.response, 'bot');
    } else {
      addBubble('Sorry, please try again.', 'bot');
    }
  } catch (e) {
    addBubble('Network error. Try again later.', 'bot');
  } finally {
    toggleSending(false);
    scrollToBottom();
  }
}

function addBubble(content, who) {
  const chat = document.getElementById('chatBody');
  const bubble = document.createElement('div');
  bubble.className = who === 'user' ?
    'self-end max-w-xl rounded-2xl px-4 py-3 my-2 bg-gray-900 text-white shadow' :
    'self-start max-w-xl rounded-2xl px-4 py-3 my-2 bg-white text-gray-900 shadow';
  bubble.innerText = content;
  chat.appendChild(bubble);
}

function scrollToBottom() {
  const wrap = document.getElementById('chatWrapper');
  wrap.scrollTop = wrap.scrollHeight;
}

function toggleSending(isSending) {
  const btn = document.getElementById('sendBtn');
  btn.disabled = isSending;
  btn.innerText = isSending ? 'Sending…' : 'Send';
}

function quickAsk(text) {
  const input = document.getElementById('userInput');
  input.value = text;
  sendMessage();
}

document.addEventListener('DOMContentLoaded', () => {
  const input = document.getElementById('userInput');
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });
});
