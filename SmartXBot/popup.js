const BACKEND_URL = "http://localhost:8000";
const STATUS_DURATION = 3000;

// Load saved prompts and keywords on popup open
async function loadSavedData() {
  try {
    // Load prompts
    const promptsResponse = await fetch(`${BACKEND_URL}/prompts`);
    if (promptsResponse.ok) {
      const promptsData = await promptsResponse.json();
      if (promptsData.hiring_prompt) {
        document.getElementById("hiringPrompt").value = promptsData.hiring_prompt;
      }
      if (promptsData.normal_prompt) {
        document.getElementById("normalPrompt").value = promptsData.normal_prompt;
      }
    }
    
    // Load keywords
    const keywordsResponse = await fetch(`${BACKEND_URL}/keywords-config`);
    if (keywordsResponse.ok) {
      const keywordsData = await keywordsResponse.json();
      if (keywordsData.keywords && keywordsData.keywords.length > 0) {
        document.getElementById("keywordsTextarea").value = keywordsData.keywords.join('\n');
      }
      if (keywordsData.since_date) {
        document.getElementById("sinceDate").value = keywordsData.since_date;
      }
      if (keywordsData.until_date) {
        document.getElementById("untilDate").value = keywordsData.until_date;
      }
    }
    
    // Enable start button if prompts are saved
    if (promptsData.hiring_prompt && promptsData.normal_prompt) {
      document.getElementById("start").disabled = false;
    }
  } catch (err) {
    console.error("Failed to load data:", err);
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

// Save prompts and keywords to backend
document.getElementById("promptForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  
  const hiringPrompt = document.getElementById("hiringPrompt").value.trim();
  const normalPrompt = document.getElementById("normalPrompt").value.trim();
  const keywordsText = document.getElementById("keywordsTextarea").value.trim();
  const sinceDate = document.getElementById("sinceDate").value;
  const untilDate = document.getElementById("untilDate").value;
  
  if (!hiringPrompt || !normalPrompt) {
    showStatus("Please fill in both prompts", "error");
    return;
  }
  
  if (!keywordsText) {
    showStatus("Please enter at least one keyword", "error");
    return;
  }
  
  try {
    // Save prompts
    const promptsResponse = await fetch(`${BACKEND_URL}/prompts`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        hiring_prompt: hiringPrompt,
        normal_prompt: normalPrompt,
      }),
    });
    
    if (!promptsResponse.ok) {
      const error = await promptsResponse.json();
      showStatus(`Error saving prompts: ${error.detail || "Failed"}`, "error");
      return;
    }
    
    // Parse keywords (split by newline, filter empty lines)
    const keywords = keywordsText
      .split('\n')
      .map(line => line.trim())
      .filter(line => line.length > 0);
    
    // Save keywords
    const keywordsResponse = await fetch(`${BACKEND_URL}/keywords-config`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        keywords: keywords,
        since_date: sinceDate || null,
        until_date: untilDate || null,
      }),
    });
    
    if (keywordsResponse.ok) {
      showStatus("All settings saved successfully!", "success");
      document.getElementById("start").disabled = false;
    } else {
      const error = await keywordsResponse.json();
      showStatus(`Error saving keywords: ${error.detail || "Failed"}`, "error");
    }
  } catch (err) {
    showStatus("Failed to connect to backend. Make sure it's running.", "error");
    console.error("Error saving data:", err);
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

// Load prompts and keywords when popup opens
loadSavedData();
