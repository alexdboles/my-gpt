# Release verification — September 7, 2026

- A fresh Python 3.12 environment installed Flask 3.1.3, Transformers 5.16.1, Torch 2.14.0 and Accelerate 1.14.0.
- BlenderBot-400M-distill weights downloaded and loaded successfully. A real `/chatbot` request returned HTTP 200 with a generated answer to a fictional hobby question.
- Unit tests cover isolated session reset, invalid requests, model failures, context budgets, response content type, and body limits. CI runs mocked inference without downloading model weights.
- Responses are plain text with no-sniff and no-store headers; chat rendering uses text nodes.

A single successful response is a runtime smoke test, not a model-quality evaluation. CPU speed and package availability vary across platforms. The app remains a local educational demonstration, not a public production service.
