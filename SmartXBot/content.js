(async () => {
  console.log("🚀 Twitter Auto Replier started (balanced mode)...");

  const KEYWORD_ENDPOINT = "http://localhost:8000/keywords";
  const TWEET_PROCESS_ENDPOINT = "http://localhost:8000/tweet-process";
  const MY_USERNAME = "its_osman2";

  const delay = (ms) => new Promise((res) => setTimeout(res, ms));
  const randomDelay = (min, max) => delay(min + Math.random() * (max - min));

  async function fetchKeywords() {
    try {
      const res = await fetch(KEYWORD_ENDPOINT);
      const data = await res.json();
      return data.keywords || [];
    } catch (err) {
      console.error("❌ Failed to fetch keywords:", err);
      return [];
    }
  }

  function shuffleArray(array) {
    for (let i = array.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [array[i], array[j]] = [array[j], array[i]];
    }
    return array;
  }

  async function searchKeyword(keyword) {
    console.log(`🔍 Searching for: ${keyword}`);
    const moreBtn = document.querySelector('[data-testid="searchBoxOverflowButton"]');
    moreBtn?.click();
    await delay(700); // moderate

    const advBtn = document.querySelector('[data-testid="advancedSearch-overflow"]');
    advBtn?.click();
    await delay(1000); // moderate

    const input = document.querySelector('input[name="allOfTheseWords"]');
    if (!input) return false;

    input.focus();
    input.value = "";
    input.dispatchEvent(new Event("input", { bubbles: true }));
    await delay(400); // normal

    for (let c of keyword) {
      input.value += c;
      input.dispatchEvent(new Event("input", { bubbles: true }));
      await delay(100); // normal typing speed for search
    }

    const btns = Array.from(document.querySelectorAll("button"));
    const searchBtn = btns.find((b) => b.textContent.toLowerCase() === "search");
    searchBtn?.click();
    await delay(3000); // short wait for results
    return true;
  }

  async function scrollToLoad(min = 50) {
    const seen = new Set();
    let tries = 0;
    while (seen.size < min && tries < 10) {
      document.querySelectorAll("article").forEach((a) => seen.add(a.innerText));
      window.scrollBy(0, 800);
      await delay(2000 + Math.random() * 1000);
      tries++;
    }
    console.log(`✅ Loaded ${seen.size} tweets`);
  }

  async function clickAndFocusReplyBox() {
    const container = document.querySelector('[data-testid="tweetTextarea_0RichTextInputContainer"]');
    if (!container) return false;

    container.click();
    await delay(400);

    const inputDiv = container.querySelector('[data-testid="tweetTextarea_0"]');
    if (!inputDiv) return false;

    inputDiv.focus();
    inputDiv.dispatchEvent(new MouseEvent("mousedown", { bubbles: true }));
    inputDiv.dispatchEvent(new MouseEvent("mouseup", { bubbles: true }));
    inputDiv.dispatchEvent(new MouseEvent("click", { bubbles: true }));
    await delay(400);

    return inputDiv;
  }

  async function typeInReplyBox(replyMessage) {
    const inputDiv = await clickAndFocusReplyBox();
    if (!inputDiv) {
      console.error("❌ Cannot find or focus reply box");
      return false;
    }

    const textSpan = inputDiv.querySelector("span[data-text='true']");
    if (textSpan) {
      textSpan.textContent = "";
    }

    for (let char of replyMessage) {
      const evt = new InputEvent("input", {
        bubbles: true,
        cancelable: true,
        inputType: "insertText",
        data: char,
      });

      document.execCommand("insertText", false, char);
      inputDiv.dispatchEvent(evt);
      await delay(80 + Math.random() * 70); // slower, human typing feel
    }

    console.log("✅ Typed message into reply box");
    return true;
  }

  function getAuthorUsername() {
    const link = document.querySelector('a[href^="/"][role="link"]');
    if (!link) return null;

    const usernameSpan = link.querySelector('span');
    if (!usernameSpan) return null;

    const username = usernameSpan.innerText.trim().replace(/^@/, '');
    return username;
  }

  async function processTweets() {
    const replied = new Set();
    let keepGoing = true;

    while (keepGoing) {
      await delay(3000);

      const articles = Array.from(document.querySelectorAll("article"));
      let foundNew = false;

      for (let article of articles) {
        const textEl = article.querySelector('[data-testid="tweetText"]');
        if (!textEl) continue;

        const tweet = textEl.innerText.trim();
        if (!tweet || replied.has(tweet)) continue;

        replied.add(tweet);
        foundNew = true;

        textEl.click();
        await delay(3000);

        const tweetId = window.location.href.split("/status/")[1]?.split("?")[0];
        if (!tweetId) {
          console.log("tweet id not found");
          document.querySelector('[data-testid="app-bar-back"]')?.click();
          await delay(3000);
          break;
        }

        let replyMessage = null;
        try {
          const res = await fetch(TWEET_PROCESS_ENDPOINT, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ tweet_id: tweetId, tweet }),
          });

          const data = await res.json();
          replyMessage = data.message;

          if (!replyMessage || replyMessage === "OLD") {
            console.log("⏩ Skipping OLD tweet");
            document.querySelector('[data-testid="app-bar-back"]')?.click();
            await delay(3000);
            break;
          }
        } catch (err) {
          console.error("❌ Backend error:", err);
          document.querySelector('[data-testid="app-bar-back"]')?.click();
          await delay(3000);
          break;
        }

        const authorUsername = getAuthorUsername();
        if (authorUsername && authorUsername.toLowerCase() === MY_USERNAME.toLowerCase()) {
          console.log("⏩ Skipping my own tweet!");
          document.querySelector('[data-testid="app-bar-back"]')?.click();
          await delay(3000);
          break;
        }

        const typed = await typeInReplyBox(replyMessage);
        if (!typed) {
          document.querySelector('[data-testid="app-bar-back"]')?.click();
          await delay(3000);
          break;
        }

        await delay(1500);
        const replyBtn = document.querySelector('[data-testid="tweetButtonInline"]');
        if (replyBtn) {
          replyBtn.click();
          console.log("✅ Replied!");
        } else {
          console.warn("❌ Reply button not found");
        }

        await delay(3000);
        document.querySelector('[data-testid="app-bar-back"]')?.click();
        await delay(3000);
        break; // process one reply per scan
      }

      if (!foundNew) {
        console.log("✅ No more new tweets for this keyword");
        keepGoing = false;
      }
    }
  }
  let i = 0
  const keywords = await fetchKeywords();
  for (const keyword of keywords) {
    const ok = await searchKeyword(keyword);
    if (!ok) continue;

    await scrollToLoad(50);
    await processTweets();

    // Short rest between keywords
    await delay(5000);
    // Every 3–4 keywords, pause for 2–3 mins
    if ((i + 1) % 3 === 0 && Math.random() > 0.3) {
      console.log("🛑 Taking a break for 2–3 minutes...");
      await randomDelay(60000, 120000);
    }
    i++;
  }

  console.log("🎉 Done (balanced mode)!");
})();
