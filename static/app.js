'use strict';

// DOM Element references
const topicDisplay = document.getElementById('topic-display');
const copyTopicBtn = document.getElementById('copy-topic-btn');
const submitBtn = document.getElementById('submit-btn');
const errorSection = document.getElementById('error-section');
const promptBox = document.getElementById('prompt-box');
const copyPromptBtn = document.getElementById('copy-prompt-btn');
const statusMessage = document.getElementById('status-message');
const mainUi = document.getElementById('main-ui');
const doneScreen = document.getElementById('done-screen');
const toastContainer = document.getElementById('toast-container');
const systemPromptBox = document.getElementById('system-prompt-box');
const copySystemPromptBtn = document.getElementById('copy-system-prompt-btn');

let currentTopic = '';

function setStatus(text, isError = false) {
  statusMessage.textContent = text;
  statusMessage.classList.toggle('error', isError);
  showToast(text);
}

function showToast(message, isError = false) {
  const toast = document.createElement('div');
  toast.className = `toast ${isError ? 'error' : ''}`;
  toast.textContent = message;
  toastContainer.appendChild(toast);

  // Trigger entrance transition
  requestAnimationFrame(() => toast.classList.add('show'));

  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 200);
  }, 4500);
}

async function copyToClipboard(text) {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (err) {
    console.warn('Clipboard write prevented by browser permissions:', err);
    return false;
  }
}

async function loadNextTopic() {
  // Clear any existing error prompts for the incoming topic
  promptBox.value = '';
  errorSection.classList.add('hidden');
  setStatus('');

  try {
    const res = await fetch('/api/topic');
    const data = await res.json();

    if (data.done) {
      mainUi.classList.add('hidden');
      doneScreen.classList.remove('hidden');
      return;
    }

    currentTopic = data.topic;
    topicDisplay.textContent = currentTopic;

    // Automatically copy the newly loaded topic
    const copied = await copyToClipboard(currentTopic);
    if (copied) {
      setStatus('Topic copied to clipboard.');
    }
  } catch (err) {
    setStatus('Failed to fetch the next topic from server.', true);
  }
}

async function loadSystemPrompt() {
  try {
    const res = await fetch('/api/system-prompt');
    const data = await res.json();
    systemPromptBox.value = data.prompt || 'Failed to load or file empty.';
  } catch (err) {
    systemPromptBox.value = 'Failed to load system prompt.';
  }
}

copySystemPromptBtn.addEventListener('click', async () => {
  if (!systemPromptBox.value) return;
  const ok = await copyToClipboard(systemPromptBox.value);
  if (ok) showToast('System prompt copied to clipboard!');
});

// Manual copy fallback for topic
copyTopicBtn.addEventListener('click', async () => {
  if (!currentTopic) return;
  await copyToClipboard(currentTopic);
  setStatus('Topic copied to clipboard.');
});

// Manual copy fallback for error prompt
copyPromptBtn.addEventListener('click', async () => {
  if (!promptBox.value) return;
  await copyToClipboard(promptBox.value);
  setStatus('Fix prompt copied to clipboard.');
});

// Main submit action
submitBtn.addEventListener('click', async () => {
  let clipboardText = '';

  try {
    clipboardText = await navigator.clipboard.readText();
  } catch (err) {
    setStatus('Clipboard access denied. Please allow clipboard permissions.', true);
    return;
  }

  if (!clipboardText.trim()) {
    setStatus('Clipboard is empty. Copy the JSON from Claude first.', true);
    return;
  }

  setStatus('Validating lesson...');

  try {
    const res = await fetch('/api/submit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        topic: currentTopic,
        json_str: clipboardText
      })
    });

    const result = await res.json();

    if (result.success) {
      await loadNextTopic();
    } else {
      // Build error prompt matching the exact format
      const fixPrompt = `\`\`\`json\n${clipboardText}\n\n\`\`\`\nthis json had the following error:\n\`\`\`\n${result.error}\n\n\`\`\`\nplease fix`;
      promptBox.value = fixPrompt;
      errorSection.classList.remove('hidden');

      await copyToClipboard(fixPrompt);
      setStatus('Validation failed. Fix prompt copied to clipboard.', true);
    }
  } catch (err) {
    setStatus(`Communication error: ${err.message}`, true);
  }
});

// Initial boot
loadSystemPrompt();
loadNextTopic();