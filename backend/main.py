from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pydantic import BaseModel
import os
from typing import Set
from ai_message import generate_final_reply

app = FastAPI()

# File to store processed tweet IDs
TWEET_ID_FILE = "processed_ids.txt"

# Load processed tweet IDs from file
def load_processed_ids() -> Set[str]:
    if not os.path.exists(TWEET_ID_FILE):
        return set()
    with open(TWEET_ID_FILE, "r") as f:
        return set(line.strip() for line in f.readlines())

# Save a tweet ID to file
def save_tweet_id(tweet_id: str):
    with open(TWEET_ID_FILE, "a") as f:
        f.write(tweet_id + "\n")

processed_tweet_ids = load_processed_ids()

# Allow Chrome Extension to call API locally
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_keywords(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        # Remove trailing newline characters and blank lines
        keywords = [line.strip() for line in file if line.strip()]
    return keywords

keyword_file = 'keywords.txt'
keywords = load_keywords(keyword_file)


class TweetRequest(BaseModel):
    tweet: str

@app.get("/keywords")
def get_keywords():
    return {"keywords": keywords}

# Input model
class TweetRequest(BaseModel):
    tweet_id: str
    tweet: str

@app.post("/tweet-process")
async def process_tweet(data: TweetRequest):
    tweet_id = data.tweet_id
    tweet_text = data.tweet.strip()

    print(f"🔍 Processing Tweet ID: {tweet_id}")
    print(f"📝 Text: {tweet_text}")

    if tweet_id in processed_tweet_ids:
        print("🕒 Already processed. Marking as OLD.")
        return {"message": "OLD"}

    reply = generate_final_reply(tweet_text)
    if len(reply) > 280:
        reply = reply[:280]
    print(f"reply::{reply}")

    # Mark as processed
    processed_tweet_ids.add(tweet_id)
    save_tweet_id(tweet_id)

    return {"message": reply}