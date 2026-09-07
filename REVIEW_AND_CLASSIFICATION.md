# Initial intake review — historical record

The findings below describe the original supplied version. Focused fixes have since been applied; README.md and VALIDATION.md describe this release. Remaining limitations are explicitly documented there.

# Project 02 — My-GPT local chatbot

## Classification
README identifies this as Module 2 of IBM Building Generative AI-Powered Applications with Python. This is separate from Project 01, the static portfolio website.

- app.py: Flask web application using BlenderBot-400M-distill.
- templates/index.html and static/script.js/style.css: matching browser interface for /chatbot and /reset.
- chatbot.py: standalone BlenderBot terminal variant; not imported by the web application.
- chatbot_llm.py: standalone SmolLM2-360M-Instruct terminal variant; not the web backend. Keep as a distinct experiment, not an assumed newer replacement.
- requirements.txt: shared dependency list; runtime compatibility has not been tested.

## Confirmed review findings
1. Global conversation_history in app.py is shared by all visitors; /reset clears it for everyone. Isolate sessions before public deployment and serialize turn/reset operations.
2. JSON requests are not validated for missing, wrong-type or oversized prompts. Add bounded validation and useful errors.
3. Browser reset ignores response status and lacks error handling; reset can race with inference and leave browser/server history inconsistent.
4. The SmolLM2 history expression duplicates the system message in early turns and later can retain an assistant-first fragment. Preserve one system message plus complete recent exchanges.
5. Model loading happens at import time; CLI modules immediately enter input loops. Add explicit entry points and recoverable loading behavior.
6. Verify each model context limit; hardcoded 512 and right-side truncation can discard the latest user input. The causal variant passes max_length without explicit truncation. Budget history in tokens and preserve the current prompt.
7. Open CORS is unnecessary for the provided same-origin interface. Bind local-only by default; document deployment separately.
8. Add accessible input labels, conversation status announcements, reduced-motion rules, and narrow-screen sizing.
9. README and page use different names (My-GPT / My LLM). Clearly document two model experiments and their limitations.

## Verification and status
All three Python files parsed successfully using ast.parse. No imports, model downloads, installation, inference, network checks or browser tests were run. This is an unchanged organized source copy; improvements remain pending. Original files are untouched.
