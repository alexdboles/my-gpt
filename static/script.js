const form = document.getElementById('chat-form');
const input = document.getElementById('prompt');
const messages = document.getElementById('messages');
const sendBtn = document.getElementById('send');
let busy = false;
const resetBtn = document.getElementById('reset');

function addRow(who, node) {
  const row = document.createElement('div');
  row.className = `row ${who}`;

  const avatar = document.createElement('div');
  avatar.className = `avatar ${who === 'user' ? 'user-avatar' : 'bot-avatar'}`;
  avatar.textContent = who === 'user' ? 'YOU' : 'AI';

  const bubble = document.createElement('div');
  bubble.className = 'bubble';
  if (typeof node === 'string') {
    bubble.textContent = node;
  } else {
    bubble.appendChild(node);
  }

  row.append(avatar, bubble);
  messages.appendChild(row);
  messages.scrollTop = messages.scrollHeight;
  return { row, bubble };
}

function typingIndicator() {
  const dots = document.createElement('span');
  dots.className = 'dots';
  dots.innerHTML = '<span></span><span></span><span></span>';
  return dots;
}

// Send the prompt to the Flask backend and return the bot's reply
async function makePostRequest(msg) {
  const url = '/chatbot';
  const requestBody = { prompt: msg };

  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(requestBody)
  });

  if (!response.ok) {
    const detail = await response.json().catch(() => ({}));
    throw new Error(detail.error || `Server responded ${response.status}`);
  }

  return await response.text();
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();

  if (busy) return;
  const text = input.value.trim();
  if (!text) return;

  addRow('user', text);
  input.value = '';
  busy = true; resetBtn.disabled = true;
  sendBtn.disabled = true;

  const pending = addRow('bot', typingIndicator());

  try {
    const reply = await makePostRequest(text);
    pending.bubble.textContent = reply;
  } catch (err) {
    pending.row.classList.add('error');
    pending.bubble.textContent = `Could not reach the server (${err.message}).`;
  } finally {
    busy = false; resetBtn.disabled = false;
    sendBtn.disabled = false;
    input.focus();
  }
});

resetBtn.addEventListener('click', async () => {
  if (busy) return;
  busy = true; sendBtn.disabled = resetBtn.disabled = true;
  try {
    const response = await fetch('/reset', {method:'POST'});
    if (!response.ok) throw new Error('Reset failed');
    messages.replaceChildren(); addRow('bot', 'Conversation cleared. Ask me something.');
  } catch { addRow('bot', 'Could not reset. Your conversation is still displayed; please retry.'); }
  finally {busy = false; sendBtn.disabled = resetBtn.disabled = false; input.focus();}
});
