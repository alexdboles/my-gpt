"""Standalone IBM model experiment. Run directly to start."""
def main():
    from transformers import AutoTokenizer, AutoModelForCausalLM
    import torch
    from conversation import recent_messages
    import warnings



    model_name = "HuggingFaceTB/SmolLM2-360M-Instruct"

    print("Loading model...")

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map="cpu",
        torch_dtype=torch.float32
    )

    messages = [
        {
            "role": "system",
            "content": "You are a helpful AI assistant. Give short and concise answers in 2-3 lines."
        }
    ]

    print("Chatbot started. Type 'exit' to quit.\n")
    while True:
        user_input = input("> ")

        if user_input.lower() == "exit":
            break

        messages.append({"role": "user", "content": user_input})

        messages = recent_messages(messages)

        limit = min(int(getattr(model.config, "max_position_embeddings", 2048)), 2048) - 60
        while len(tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=True)) > limit:
            if len(messages) <= 2:
                break
            del messages[1:3]
        if len(tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=True)) > limit:
            print("Message too long; please shorten it.")
            messages.pop()
            continue

        tokenized = tokenizer.apply_chat_template(
            messages,
            tokenize=True,
            add_generation_prompt=True,
            return_tensors="pt",
            return_dict=True,
        )

        with torch.inference_mode():
            outputs = model.generate(
                tokenized["input_ids"],
                attention_mask=tokenized["attention_mask"],
                max_new_tokens=60,
                temperature=0.5,
                top_p=0.8,
                do_sample=True,
                repetition_penalty=1.3,
                no_repeat_ngram_size=3,
                pad_token_id=tokenizer.pad_token_id
            )

        response = tokenizer.decode(
            outputs[0][tokenized["input_ids"].shape[-1]:],
            skip_special_tokens=True
        )

        print(f"Bot: {response}\n")

        messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()
