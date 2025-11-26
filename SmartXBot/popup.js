const BACKEND_URL = "http://localhost:8000";
const STATUS_DURATION = 3000;

// Load saved prompts on popup open
async function loadSavedPrompts() {
  try {
    const response = await fetch(`${BACKEND_URL}/prompts`);
    if (response.ok) {
      const data = await response.json();
      if (data.hiring_prompt) {
        document.getElementById("hiringPrompt").value = data.hiring_prompt;
      }
      if (data.normal_prompt) {
        document.getElementById("normalPrompt").value = data.normal_prompt;
      }
      // Enable start button if prompts are saved
      if (data.hiring_prompt && data.normal_prompt) {
        document.getElementById("start").disabled = false;
      }
    }
  } catch (err) {
    console.error("Failed to load prompts:", err);
  }
}

// Show status message
function showStatus(message, type = "success") {
  const statusEl = document.getElementById("status");
  statusEl.textContent = message;
  statusEl.className = `status ${type}`;
  setTimeout(() => {
    statusEl.className = "status";
  }, STATUS_DURATION);
}

// Save prompts to backend
document.getElementById("promptForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  
  const hiringPrompt = document.getElementById("hiringPrompt").value.trim();
  const normalPrompt = document.getElementById("normalPrompt").value.trim();
  
  if (!hiringPrompt || !normalPrompt) {
    showStatus("Please fill in both prompts", "error");
    return;
  }
  
  try {
    const response = await fetch(`${BACKEND_URL}/prompts`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        hiring_prompt: hiringPrompt,
        normal_prompt: normalPrompt,
      }),
    });
    
    if (response.ok) {
      showStatus("Prompts saved successfully!", "success");
      document.getElementById("start").disabled = false;
    } else {
      const error = await response.json();
      showStatus(`Error: ${error.detail || "Failed to save prompts"}`, "error");
    }
  } catch (err) {
    showStatus("Failed to connect to backend. Make sure it's running.", "error");
    console.error("Error saving prompts:", err);
  }
});

// Start bot button (in form)
document.getElementById("start").addEventListener("click", async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  
  if (!tab) {
    showStatus("Please open a Twitter/X tab first", "error");
    return;
  }
  
  chrome.scripting.executeScript({
    target: { tabId: tab.id },
    files: ["content.js"]
  });
  
  showStatus("Bot started! Check the console for logs.", "success");
});

// Load prompts when popup opens
loadSavedPrompts();
