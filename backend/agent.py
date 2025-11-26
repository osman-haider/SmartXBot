import ollama
import re


def clean_reply(text: str) -> str:
    text = re.sub(r"#\S+", "", text)
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^\w\s,.!?']", "", text)
    return text.strip()


def classify_tweet(tweet_text: str) -> str:
    """Classifier Agent decides if tweet is hiring or normal"""
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
    response = ollama.chat(model="mistral", messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": tweet_text}
    ])
    return response['message']['content'].strip().lower()


def drafting_agent(tweet_text: str) -> str:
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


def refining_agent(tweet_text: str, draft_reply: str) -> str:
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
    response = ollama.chat(model="mistral", messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Original Tweet: {tweet_text}\nDraft Reply: {draft_reply}"}
    ])
    return clean_reply(response['message']['content'])


EMAIL = "osmanhaider167@gmail.com"


def pitch_generator(tweet_text: str) -> str:
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
    response = ollama.chat(model="mistral", messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": tweet_text}
    ])
    return clean_reply(response['message']['content']).replace("{email}", EMAIL)


def pitch_refiner(tweet_text: str, draft_reply: str) -> str:
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
    response = ollama.chat(model="mistral", messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Tweet: {tweet_text}\nDraft Reply: {draft_reply}\n\nRefined Reply:"}
    ])
    return clean_reply(response['message']['content']).replace("{email}", EMAIL)


def pitch_agent(tweet_text: str) -> str:
    draft = pitch_generator(tweet_text)
    return pitch_refiner(tweet_text, draft)


def generate_reply(tweet_text: str) -> str:
    classification = classify_tweet(tweet_text)
    print("Classification:", classification)
    if "hiring" in classification:
        return pitch_agent(tweet_text)
    else:
        draft = drafting_agent(tweet_text)
        return refining_agent(tweet_text, draft)


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