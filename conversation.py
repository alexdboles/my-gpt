"""Small, testable context helpers shared by the course experiments."""
def recent_messages(messages, pairs=5):
    system = next((m for m in messages if m["role"] == "system"), None)
    turns = [m for m in messages if m["role"] != "system"][-(pairs * 2 + 1):]
    while turns and turns[0]["role"] != "user":
        turns.pop(0)
    return ([system] if system else []) + turns

def fit_prompt(tokenizer, history, current, limit):
    prompt = f"User: {current}\nBot:"
    if len(tokenizer.encode(prompt)) > limit:
        raise ValueError("Message is too long for this model. Please shorten it.")
    for exchange in reversed(history):
        candidate = exchange + "\n" + prompt
        if len(tokenizer.encode(candidate)) > limit:
            break
        prompt = candidate
    return prompt
