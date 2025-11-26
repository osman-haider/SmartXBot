from agent import generate_reply


# === MAIN FLOW ===
def generate_final_reply(tweet_text: str, user_prompts: dict = None) -> str:
    print(f"\n[AI_MESSAGE] {'='*60}")
    print(f"[AI_MESSAGE] 🚀 Starting generate_final_reply()")
    print(f"[AI_MESSAGE] 📝 Tweet text: {tweet_text[:100]}..." if len(tweet_text) > 100 else f"[AI_MESSAGE] 📝 Tweet text: {tweet_text}")
    print(f"[AI_MESSAGE] 📏 Tweet length: {len(tweet_text)} characters")
    
    if user_prompts:
        has_hiring = user_prompts.get("hiring_prompt") is not None
        has_normal = user_prompts.get("normal_prompt") is not None
        print(f"[AI_MESSAGE] 📋 User prompts provided - Hiring: {'✅' if has_hiring else '❌'}, Normal: {'✅' if has_normal else '❌'}")
    else:
        print(f"[AI_MESSAGE] ⚠️  No user prompts provided. Will use default prompts.")
    
    print(f"[AI_MESSAGE] ➡️  Calling generate_reply() from agent module...")
    reply = generate_reply(tweet_text, user_prompts)
    print(f"[AI_MESSAGE] ✅ Received reply from agent")
    print(f"[AI_MESSAGE] 📝 Final Reply:\n{reply}")
    print(f"[AI_MESSAGE] 📏 Reply length: {len(reply)} characters")
    print(f"[AI_MESSAGE] {'='*60}\n")

    return reply