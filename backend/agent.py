import ollama
import re


def clean_reply(text: str) -> str:
    print(f"[AGENT] 🧹 Cleaning reply text...")
    original_length = len(text)
    text = re.sub(r"#\S+", "", text)
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^\w\s,.!?']", "", text)
    cleaned = text.strip()
    print(f"[AGENT] ✅ Cleaned reply - Original: {original_length} chars, Cleaned: {len(cleaned)} chars")
    return cleaned


def classify_tweet(tweet_text: str) -> str:
    """Classifier Agent decides if tweet is hiring or normal"""
    print(f"\n[AGENT] {'='*60}")
    print(f"[AGENT] 🔍 Starting classify_tweet()")
    print(f"[AGENT] 📝 Tweet text: {tweet_text[:100]}..." if len(tweet_text) > 100 else f"[AGENT] 📝 Tweet text: {tweet_text}")
    print(f"[AGENT] 🤖 Calling Ollama model 'mistral' for classification...")
    system_prompt = """
        You are a precise text classifier that reads one tweet and decides if it is about *hiring/collaboration* or not.

        Output must be exactly one word:
        - "hiring"
        - "normal"

        ---

        ### 🔹 Definition of "hiring"
        Classify as "hiring" if the tweet:
        - Offers a job, gig, contract, freelance, or paid/unpaid opportunity
        - Seeks help, collaboration, or a developer/designer/engineer to work on a project
        - Mentions hiring roles, openings, or looking for someone specific to join a team or project

        Key signal phrases (examples):
        - "looking for someone to..."
        - "need a developer / designer / engineer / freelancer..."
        - "we are hiring", "job opening", "contract role"
        - "anyone available to help with...", "can someone build...", "DM if interested"

        ### 🔹 Definition of "normal"
        Classify as "normal" if the tweet:
        - Is about the author’s own job search ("open to work", "need a job")
        - Is general discussion, opinion, learning, or tech sharing
        - Is motivational, meme, or personal post
        - Mentions career topics without offering or requesting collaboration

        ---

        ### 🔹 Examples

        **Label: hiring**
        1. "We’re looking for a Python dev to help with a side project."
        2. "Anyone available for a small freelance ML gig?"
        3. "Hiring backend engineers — remote, full-time."
        4. "Need someone to fine-tune an LLM for my startup."
        5. "Looking for a designer to collaborate on a product launch."

        **Label: normal**
        1. "Finally wrapped up my data science course!"
        2. "I'm open to new roles in AI/ML."
        3. "Building a new RAG pipeline this weekend."
        4. "Here's a thread on why LLMs struggle with reasoning."
        5. "My team is amazing — proud of what we built."

        ---

        Rules:
        - Tweets that *offer* or *seek help for a project* → "hiring"
        - Tweets that *announce personal availability* → "normal"
        - Tweets that are ambiguous but mention “need someone”, “looking for help”, or “can you help with” → treat as "hiring"
        - Output only one word: "hiring" or "normal" — no explanation, no punctuation.
    """
    try:
        response = ollama.chat(model="mistral", messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": tweet_text}
        ])
        classification = response['message']['content'].strip().lower()
        print(f"[AGENT] ✅ Classification received: '{classification}'")
        print(f"[AGENT] {'='*60}\n")
        return classification
    except Exception as e:
        print(f"[AGENT] ❌ Error during classification: {e}")
        print(f"[AGENT] ⚠️  Defaulting to 'normal'")
        print(f"[AGENT] {'='*60}\n")
        return "normal"


def drafting_agent(tweet_text: str, normal_prompt: str = None) -> str:
    print(f"\n[AGENT] {'='*60}")
    print(f"[AGENT] ✍️  Starting drafting_agent()")
    print(f"[AGENT] 📝 Tweet text: {tweet_text[:100]}..." if len(tweet_text) > 100 else f"[AGENT] 📝 Tweet text: {tweet_text}")
    
    if normal_prompt:
        print(f"[AGENT] ✅ Using CUSTOM normal prompt (length: {len(normal_prompt)} chars)")
        system_prompt = normal_prompt
    else:
        print(f"[AGENT] ⚠️  Using DEFAULT normal prompt")
        system_prompt = """
    You write casual Twitter replies that sound completely natural and human.

    How real people reply on Twitter:
    - They're brief and conversational, like texting a friend
    - They use lowercase sometimes, incomplete sentences, casual punctuation
    - They might start with "lol", "tbh", "ngl", "honestly", "wait", "omg"
    - They relate personally: "this happened to me", "i feel this", "same here"
    - They add light humor or relatability, not forced jokes
    - They use everyday words, never corporate speak
    - Sometimes they're just reactive: "this is so true", "fr fr", "real"

    What to AVOID (these scream AI):
    - Formal greetings like "Great point!" or "Thanks for sharing!"
    - Words like: delve, leverage, utilize, keen, thrilled, innovative
    - Perfectly structured sentences with proper grammar everywhere
    - Ending with questions that feel forced
    - Generic engagement bait
    - Being overly enthusiastic or positive

    Rules:
    - Under 280 characters
    - No hashtags, emojis, or links
    - Sound like a real person scrolling Twitter, not a brand
    - Be authentic, not polished
    """
    response = ollama.chat(model="mistral", messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": tweet_text}
    ])
    return clean_reply(response['message']['content'])


def refining_agent(tweet_text: str, draft_reply: str, normal_prompt: str = None) -> str:
    print(f"\n[AGENT] {'='*60}")
    print(f"[AGENT] ✨ Starting refining_agent()")
    print(f"[AGENT] 📝 Original tweet: {tweet_text[:80]}..." if len(tweet_text) > 80 else f"[AGENT] 📝 Original tweet: {tweet_text}")
    print(f"[AGENT] 📝 Draft reply: {draft_reply[:80]}..." if len(draft_reply) > 80 else f"[AGENT] 📝 Draft reply: {draft_reply}")
    print(f"[AGENT] 📏 Draft length: {len(draft_reply)} characters")
    
    if normal_prompt:
        print(f"[AGENT] ✅ Using CUSTOM normal prompt for refining (length: {len(normal_prompt)} chars)")
        # Use the normal prompt as base, but adapt it for refining
        system_prompt = f"""
    {normal_prompt}
    
    You are refining a draft reply. Make it sound more human and natural:
    - Remove overly formal language
    - Vary sentence length (short punchy sentences are good)
    - Add conversational flow
    - Keep it casual but not trying too hard
    - Make sure it sounds like something you'd actually say out loud

    Rules:
    - Under 280 characters
    - No hashtags, emojis, or links
    - Should pass as a regular person's tweet
    - Output ONLY the final reply text
    """
    else:
        print(f"[AGENT] ⚠️  Using DEFAULT refining prompt")
        system_prompt = """
    You refine Twitter replies to make them sound more human and less AI-generated.

    Make it natural by:
    - Removing overly formal language
    - Varying sentence length (short punchy sentences are good)
    - Adding conversational flow
    - Keeping it casual but not trying too hard
    - Making sure it sounds like something you'd actually say out loud

    Red flags to remove:
    - "Great question", "Thanks for sharing", "Appreciate you"
    - Perfect punctuation and capitalization everywhere
    - Sentences that sound like LinkedIn posts
    - Forced positivity or enthusiasm

    Rules:
    - Under 280 characters
    - No hashtags, emojis, or links
    - Should pass as a regular person's tweet
    - Output ONLY the final reply text
    """
    print(f"[AGENT] 🤖 Calling Ollama model 'mistral' for refinement...")
    try:
        response = ollama.chat(model="mistral", messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Original Tweet: {tweet_text}\nDraft Reply: {draft_reply}"}
        ])
        refined = response['message']['content']
        print(f"[AGENT] ✅ Refined reply received (length: {len(refined)} chars)")
        cleaned = clean_reply(refined)
        print(f"[AGENT] ✅ Refined reply cleaned and ready")
        print(f"[AGENT] {'='*60}\n")
        return cleaned
    except Exception as e:
        print(f"[AGENT] ❌ Error during refinement: {e}")
        print(f"[AGENT] {'='*60}\n")
        raise


EMAIL = "osmanhaider167@gmail.com"


def pitch_generator(tweet_text: str, hiring_prompt: str = None) -> str:
    print(f"\n[AGENT] {'='*60}")
    print(f"[AGENT] 💼 Starting pitch_generator()")
    print(f"[AGENT] 📝 Tweet text: {tweet_text[:100]}..." if len(tweet_text) > 100 else f"[AGENT] 📝 Tweet text: {tweet_text}")
    
    if hiring_prompt:
        print(f"[AGENT] ✅ Using CUSTOM hiring prompt (length: {len(hiring_prompt)} chars)")
        system_prompt = hiring_prompt
    else:
        print(f"[AGENT] ⚠️  Using DEFAULT hiring prompt")
        system_prompt = """
    You're Usman Haider, a Data Scientist with 2.5 years experience, replying to a hiring tweet.

    Your background:
    - Data Science & Machine Learning
    - Python, RAG pipelines, LLMs, AI Agents
    - Web scraping, automation, AI solutions

    How to write your reply:
    - Start naturally: "Hey, I'm Usman..." or "Hi, I'm Usman..."
    - Keep it simple and humble, like you're DMing someone
    - Mention 1-2 relevant skills that match what they need
    - Don't oversell: no "passionate", "excited", "thrilled", "keen", "eager"
    - Write like a regular developer, not a salesperson
    - End with: "You can reach me at {email}"

    Bad example: "Hi there! I'm a seasoned data scientist with a passion for..."
    Good example: "Hey, I'm Usman, been doing data science for 2+ years. I've worked with..."

    Rules:
    - Under 280 characters
    - No hashtags, emojis, or links
    - Sound professional but relaxed
    - Keep {email} as is (don't change it)
    """
    print(f"[AGENT] 🤖 Calling Ollama model 'mistral' for pitch generation...")
    try:
        response = ollama.chat(model="mistral", messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": tweet_text}
        ])
        pitch = response['message']['content']
        print(f"[AGENT] ✅ Pitch draft received (length: {len(pitch)} chars)")
        cleaned = clean_reply(pitch)
        final_pitch = cleaned.replace("{email}", EMAIL)
        print(f"[AGENT] ✅ Email placeholder replaced with: {EMAIL}")
        print(f"[AGENT] ✅ Pitch generated and ready")
        print(f"[AGENT] {'='*60}\n")
        return final_pitch
    except Exception as e:
        print(f"[AGENT] ❌ Error during pitch generation: {e}")
        print(f"[AGENT] {'='*60}\n")
        raise


def pitch_refiner(tweet_text: str, draft_reply: str) -> str:
    print(f"\n[AGENT] {'='*60}")
    print(f"[AGENT] ✨ Starting pitch_refiner()")
    print(f"[AGENT] 📝 Original tweet: {tweet_text[:80]}..." if len(tweet_text) > 80 else f"[AGENT] 📝 Original tweet: {tweet_text}")
    print(f"[AGENT] 📝 Draft pitch: {draft_reply[:80]}..." if len(draft_reply) > 80 else f"[AGENT] 📝 Draft pitch: {draft_reply}")
    print(f"[AGENT] 📏 Draft length: {len(draft_reply)} characters")
    print(f"[AGENT] ⚠️  Using DEFAULT pitch refiner prompt")
    system_prompt = f"""
    You refine job pitch replies to sound more natural and human.

    Requirements:
    - Must start with "Hi, I'm Usman Haider" or "Hey, I'm Usman Haider" (nothing else)
    - Use simple, natural sentences like you're texting
    - Sound confident but not cocky
    - No corporate buzzwords or AI-sounding phrases

    Words/phrases to REMOVE:
    - seasoned, passionate, thrilled, excited, eager, keen, delighted
    - "I'd love to", "I'd be happy to", "looking forward to"
    - "expertise", "extensive experience", "proven track record"
    - "let's connect", "feel free to reach out"

    Write like a normal developer:
    - "I've been working with X for Y years"
    - "I've built projects using..."
    - "I have experience in..."
    - Keep it factual and straightforward

    Rules:
    - Under 280 characters
    - No hashtags, emojis, or links
    - Email must appear exactly once at the end: {EMAIL}
    - Should sound like a real person, not a cover letter
    """
    print(f"[AGENT] 🤖 Calling Ollama model 'mistral' for pitch refinement...")
    try:
        response = ollama.chat(model="mistral", messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Tweet: {tweet_text}\nDraft Reply: {draft_reply}\n\nRefined Reply:"}
        ])
        refined = response['message']['content']
        print(f"[AGENT] ✅ Refined pitch received (length: {len(refined)} chars)")
        cleaned = clean_reply(refined)
        final_pitch = cleaned.replace("{email}", EMAIL)
        print(f"[AGENT] ✅ Email placeholder replaced with: {EMAIL}")
        print(f"[AGENT] ✅ Pitch refined and ready")
        print(f"[AGENT] {'='*60}\n")
        return final_pitch
    except Exception as e:
        print(f"[AGENT] ❌ Error during pitch refinement: {e}")
        print(f"[AGENT] {'='*60}\n")
        raise


def pitch_agent(tweet_text: str, hiring_prompt: str = None) -> str:
    print(f"\n[AGENT] {'='*60}")
    print(f"[AGENT] 💼 Starting pitch_agent() - Full hiring flow")
    print(f"[AGENT] 📋 Hiring prompt provided: {'✅ Yes' if hiring_prompt else '❌ No (using default)'}")
    
    print(f"[AGENT] 🔄 Step 1/2: Generating pitch draft...")
    draft = pitch_generator(tweet_text, hiring_prompt)
    print(f"[AGENT] ✅ Pitch draft generated")
    
    print(f"[AGENT] 🔄 Step 2/2: Refining pitch...")
    refined = pitch_refiner(tweet_text, draft)
    print(f"[AGENT] ✅ Pitch agent completed")
    print(f"[AGENT] {'='*60}\n")
    return refined


def generate_reply(tweet_text: str, user_prompts: dict = None) -> str:
    print(f"\n[AGENT] {'='*60}")
    print(f"[AGENT] 🚀 Starting generate_reply()")
    print(f"[AGENT] 📝 Tweet text: {tweet_text[:100]}..." if len(tweet_text) > 100 else f"[AGENT] 📝 Tweet text: {tweet_text}")
    
    # Extract prompts if provided
    hiring_prompt = None
    normal_prompt = None
    if user_prompts:
        print(f"[AGENT] 📋 User prompts provided")
        hiring_prompt = user_prompts.get("hiring_prompt")
        normal_prompt = user_prompts.get("normal_prompt")
        print(f"[AGENT] 📋 Hiring prompt: {'✅ Provided' if hiring_prompt else '❌ Not provided (will use default)'}")
        print(f"[AGENT] 📋 Normal prompt: {'✅ Provided' if normal_prompt else '❌ Not provided (will use default)'}")
    else:
        print(f"[AGENT] ⚠️  No user prompts provided. Will use all default prompts.")
    
    print(f"[AGENT] 🔍 Step 1: Classifying tweet...")
    classification = classify_tweet(tweet_text)
    print(f"[AGENT] ✅ Classification result: '{classification}'")
    
    if "hiring" in classification:
        print(f"[AGENT] 💼 Tweet classified as HIRING → Using pitch_agent()")
        reply = pitch_agent(tweet_text, hiring_prompt)
        print(f"[AGENT] ✅ Hiring reply generated")
    else:
        print(f"[AGENT] 💬 Tweet classified as NORMAL → Using drafting + refining agents")
        print(f"[AGENT] 🔄 Step 1/2: Generating draft...")
        draft = drafting_agent(tweet_text, normal_prompt)
        print(f"[AGENT] ✅ Draft generated")
        print(f"[AGENT] 🔄 Step 2/2: Refining draft...")
        reply = refining_agent(tweet_text, draft, normal_prompt)
        print(f"[AGENT] ✅ Normal reply generated")
    
    print(f"[AGENT] ✅ generate_reply() completed")
    print(f"[AGENT] 📝 Final reply: {reply[:100]}..." if len(reply) > 100 else f"[AGENT] 📝 Final reply: {reply}")
    print(f"[AGENT] 📏 Reply length: {len(reply)} characters")
    print(f"[AGENT] {'='*60}\n")
    return reply


if __name__ == "__main__":
    tweet = """
if you are exprt in ai i have a project idea we can work together on it
"""
    import time

    start_time = time.time()
    reply = generate_reply(tweet)
    end_time = time.time()
    print(f"Time taken: {end_time - start_time:.2f} seconds")
    print("Tweet:", tweet)
    print("AI Reply:", reply)