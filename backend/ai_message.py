from agent import generate_reply


# === MAIN FLOW ===
def generate_final_reply(tweet_text: str) -> str:
    print("➡️ Agent Generating initial reply...")
    reply = generate_reply(tweet_text)
    print(f"\n📝 Initial Reply:\n{reply}")

    return reply