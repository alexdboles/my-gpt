# My-GPT — IBM local chatbot exercise

IBM Building Generative AI-Powered Applications with Python, Module 2, with focused reliability fixes. This is a learning project, not a production assistant.

## Three entry points
- `python app.py`: Flask web UI and local BlenderBot-400M-distill inference.
- `python chatbot.py`: standalone BlenderBot terminal experiment.
- `python chatbot_llm.py`: standalone SmolLM2-360M-Instruct terminal experiment.

The terminal variants are separate experiments, not replacements for the web backend. Their imports do not start downloads or interactive sessions.

## Setup
Use **Python 3.12**. The pinned dependency set was installed and tested on macOS ARM64. PyTorch support depends on your operating system; a 64-bit desktop is required.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

Open http://localhost:5001. Model weights download from Hugging Face on first use; a real BlenderBot response was verified in this release on macOS ARM64. Allow several GB of disk space for dependencies and model caches. No API key is required. First inference can take time. The optional FLASK_SECRET_KEY environment variable stabilizes signed session cookies across runs; otherwise a random local key is created each start.

## Scope and changes
The web model loads lazily; histories are isolated by signed session ID, capped to three exchanges and expire after inactivity. Generation/reset share a lock to prevent races. This intentionally simple single-process demo serializes inference and loses histories on restart. It is not designed for public multi-worker hosting.

Input is validated and token-budgeted against model capacity. New questions are preserved; oversized questions receive an error. SmolLM2 keeps exactly one system message and whole recent exchanges. Reset failures preserve the displayed conversation. Rendering treats user content as text.

Local model outputs can be inaccurate. The interface is a learning demonstration, with a named input and announced messages. See VALIDATION.md for checks and limitations.

## Tests
Install `requirements-test.txt`, then run `python -m unittest discover -s tests -v`. Tests mock inference and do not download models.

## Identity and attribution

“My-GPT” is the course-project name. This app uses Hugging Face BlenderBot and SmolLM2, not an OpenAI GPT model or ChatGPT account. Model files download from Hugging Face; subsequent inference runs locally. IBM course material is not redistributed and IBM does not endorse this portfolio project.

## Data and hosting limits

Conversations live only in this process's memory and expire after an hour of inactivity. Reset clears the current session. This is a loopback-only learning app, not a public chat service. It has no account management, multi-worker shared state, or production abuse controls. Keep it bound to `127.0.0.1`.
