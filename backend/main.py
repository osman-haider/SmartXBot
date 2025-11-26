from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pydantic import BaseModel
import os
import json
from typing import Set, Optional
from ai_message import generate_final_reply

app = FastAPI()

# File to store processed tweet IDs
TWEET_ID_FILE = "processed_ids.txt"
# File to store user prompts
PROMPTS_FILE = "user_prompts.json"

# Load processed tweet IDs from file
def load_processed_ids() -> Set[str]:
    print(f"[MAIN] 📂 Loading processed tweet IDs from {TWEET_ID_FILE}")
    if not os.path.exists(TWEET_ID_FILE):
        print(f"[MAIN] ⚠️  File {TWEET_ID_FILE} does not exist. Starting with empty set.")
        return set()
    with open(TWEET_ID_FILE, "r") as f:
        ids = set(line.strip() for line in f.readlines())
        print(f"[MAIN] ✅ Loaded {len(ids)} processed tweet IDs")
        return ids

# Save a tweet ID to file
def save_tweet_id(tweet_id: str):
    print(f"[MAIN] 💾 Saving tweet ID: {tweet_id} to {TWEET_ID_FILE}")
    with open(TWEET_ID_FILE, "a") as f:
        f.write(tweet_id + "\n")
    print(f"[MAIN] ✅ Tweet ID saved successfully")

print("[MAIN] 🚀 Initializing backend...")
processed_tweet_ids = load_processed_ids()
print(f"[MAIN] ✅ Backend initialized with {len(processed_tweet_ids)} processed tweets")

# Allow Chrome Extension to call API locally
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_keywords(file_path):
    print(f"[MAIN] 📂 Loading keywords from {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            # Remove trailing newline characters and blank lines
            keywords = [line.strip() for line in file if line.strip()]
        print(f"[MAIN] ✅ Loaded {len(keywords)} keywords")
        return keywords
    except Exception as e:
        print(f"[MAIN] ❌ Error loading keywords: {e}")
        return []

keyword_file = 'keywords.txt'
keywords = load_keywords(keyword_file)

# Load user prompts from file
def load_user_prompts() -> dict:
    print(f"[MAIN] 📂 Loading user prompts from {PROMPTS_FILE}")
    if not os.path.exists(PROMPTS_FILE):
        print(f"[MAIN] ⚠️  Prompts file {PROMPTS_FILE} does not exist. Using default prompts.")
        return {"hiring_prompt": None, "normal_prompt": None}
    try:
        with open(PROMPTS_FILE, "r", encoding="utf-8") as f:
            prompts = json.load(f)
            has_hiring = prompts.get("hiring_prompt") is not None
            has_normal = prompts.get("normal_prompt") is not None
            print(f"[MAIN] ✅ Loaded prompts - Hiring: {'✅' if has_hiring else '❌'}, Normal: {'✅' if has_normal else '❌'}")
            return prompts
    except Exception as e:
        print(f"[MAIN] ❌ Error loading prompts: {e}. Using default prompts.")
        return {"hiring_prompt": None, "normal_prompt": None}

# Save user prompts to file
def save_user_prompts(hiring_prompt: str, normal_prompt: str):
    print(f"[MAIN] 💾 Saving user prompts to {PROMPTS_FILE}")
    print(f"[MAIN] 📝 Hiring prompt length: {len(hiring_prompt)} characters")
    print(f"[MAIN] 📝 Normal prompt length: {len(normal_prompt)} characters")
    prompts = {
        "hiring_prompt": hiring_prompt,
        "normal_prompt": normal_prompt
    }
    try:
        with open(PROMPTS_FILE, "w", encoding="utf-8") as f:
            json.dump(prompts, f, indent=2)
        print(f"[MAIN] ✅ Prompts saved successfully")
    except Exception as e:
        print(f"[MAIN] ❌ Error saving prompts: {e}")

# Initialize prompts
print("[MAIN] 🔄 Initializing user prompts...")
user_prompts = load_user_prompts()

@app.get("/keywords")
def get_keywords():
    print(f"[MAIN] 📡 GET /keywords endpoint called")
    print(f"[MAIN] 📤 Returning {len(keywords)} keywords")
    return {"keywords": keywords}

# Prompts model
class PromptsRequest(BaseModel):
    hiring_prompt: str
    normal_prompt: str

@app.post("/prompts")
async def save_prompts(data: PromptsRequest):
    """Save user-provided prompts"""
    print(f"[MAIN] 📡 POST /prompts endpoint called")
    print(f"[MAIN] 📥 Received hiring prompt: {len(data.hiring_prompt)} characters")
    print(f"[MAIN] 📥 Received normal prompt: {len(data.normal_prompt)} characters")
    save_user_prompts(data.hiring_prompt, data.normal_prompt)
    # Update global prompts
    user_prompts["hiring_prompt"] = data.hiring_prompt
    user_prompts["normal_prompt"] = data.normal_prompt
    print(f"[MAIN] ✅ Global prompts updated")
    print(f"[MAIN] 📤 Returning success response")
    return {"message": "Prompts saved successfully"}

@app.get("/prompts")
def get_prompts():
    """Get saved user prompts"""
    print(f"[MAIN] 📡 GET /prompts endpoint called")
    prompts = load_user_prompts()
    has_hiring = prompts.get("hiring_prompt") is not None
    has_normal = prompts.get("normal_prompt") is not None
    print(f"[MAIN] 📤 Returning prompts - Hiring: {'✅' if has_hiring else '❌'}, Normal: {'✅' if has_normal else '❌'}")
    return prompts

# Input model
class TweetRequest(BaseModel):
    tweet_id: str
    tweet: str

@app.post("/tweet-process")
async def process_tweet(data: TweetRequest):
    print(f"\n{'='*60}")
    print(f"[MAIN] 📡 POST /tweet-process endpoint called")
    print(f"{'='*60}")
    tweet_id = data.tweet_id
    tweet_text = data.tweet.strip()

    print(f"[MAIN] 🔍 Processing Tweet ID: {tweet_id}")
    print(f"[MAIN] 📝 Tweet Text: {tweet_text}")
    print(f"[MAIN] 📏 Tweet length: {len(tweet_text)} characters")

    print(f"[MAIN] 🔍 Checking if tweet ID {tweet_id} is already processed...")
    if tweet_id in processed_tweet_ids:
        print(f"[MAIN] ⚠️  Tweet ID {tweet_id} already in processed set")
        print(f"[MAIN] 🕒 Already processed. Marking as OLD.")
        print(f"[MAIN] 📤 Returning OLD response")
        return {"message": "OLD"}

    print(f"[MAIN] ✅ Tweet ID {tweet_id} is new. Proceeding with processing...")
    
    # Get current prompts (in case they were updated)
    print(f"[MAIN] 🔄 Loading current prompts...")
    current_prompts = load_user_prompts()
    has_hiring = current_prompts.get("hiring_prompt") is not None
    has_normal = current_prompts.get("normal_prompt") is not None
    print(f"[MAIN] 📋 Prompts status - Hiring: {'✅ Custom' if has_hiring else '⚠️  Default'}, Normal: {'✅ Custom' if has_normal else '⚠️  Default'}")

    print(f"[MAIN] 🤖 Calling generate_final_reply()...")
    reply = generate_final_reply(tweet_text, current_prompts)
    
    print(f"[MAIN] 📏 Generated reply length: {len(reply)} characters")
    if len(reply) > 280:
        print(f"[MAIN] ⚠️  Reply exceeds 280 characters. Truncating...")
        reply = reply[:280]
        print(f"[MAIN] ✅ Truncated to {len(reply)} characters")
    
    print(f"[MAIN] 📝 Final Reply: {reply}")

    # Mark as processed
    print(f"[MAIN] 💾 Marking tweet ID {tweet_id} as processed...")
    processed_tweet_ids.add(tweet_id)
    save_tweet_id(tweet_id)
    print(f"[MAIN] ✅ Tweet ID {tweet_id} marked as processed")

    print(f"[MAIN] 📤 Returning reply to client")
    print(f"{'='*60}\n")
    return {"message": reply}