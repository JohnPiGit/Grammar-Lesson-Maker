# Japanese Grammar Lesson Generator

A lightweight, local web tool for generating, validating, and compiling Japanese grammar lessons one topic at a time using an LLM and browser clipboard automation (i.e. I don't want to pay for AI...).

Minimally cobbled together project for making lessons for https://github.com/JohnPiGit/Japanese-Grammar-Server

---

## Features

- **Clipboard Automation:** Automatically copies missing grammar topics to your clipboard on load and reads generated JSON directly from your clipboard upon submission.
- **Smart Queueing:** Compares topics in `grammar_topics.txt` against `lessons.json` and serve only unfinished topics (hashes the topic with sha256 to use as a key cuz why not).
- **Instant Error Feedback:** If validation fails, automatically formats and copies a prompt containing the JSON and error message ready to paste back into an LLM for correction (Highly recommend a cheaper/dumber model as json correction is an easy task... save your precious tokens).
- **Zero External Dependencies:** Built with Python's standard library and vanilla HTML/CSS/JavaScript.

---

## File Structure

```text
.
├── server.py                   # Local web server & API
├── jp_lesson.py                # Validation & storage logic (try_check_json)
├── generate_lesson_prompt.md   # LLM system prompt instructions
├── grammar_topics.txt          # Newline-delimited list of grammar topics
├── lessons.json                # Master JSON database (SHA-256 keyed)
└── static/
    ├── index.html              # UI markup & instructions
    ├── style.css               # Minimal styling & toast notifications
    └── app.js                  # Frontend clipboard & API orchestration
```

---

## Getting Started

### Prerequisites

- Python 3.9+
- A modern web browser (Chrome, Firefox, Edge, Safari) that supports the Clipboard API.

### Running the Server

From the project root:

```bash
python server.py
```

Open **`http://localhost:8000`** in your browser. When prompted, grant clipboard permissions.

---

## Workflow

1. **Set Up System Prompt:** Click **Copy System Prompt** and paste it into your chat session (paste it into a system prompt box if you can).
2. **Send Topic:** The active grammar topic is automatically copied to your clipboard on load. Paste it as a prompt into your LLM.
3. **Submit Lesson:** Copy the JSON response from your LLM, return to the browser, and click **Read Clipboard & Submit**.
4. **Handle Errors (if any):** If the schema check fails, the `fix-me prompt` is automatically formatted and copied to your clipboard. Paste it into an LLM to correct the JSON, copy the fix, and submit again.
5. **Repeat:** On success, the lesson is saved to `lessons.json` and the next missing topic is automatically copied. Clear your chat history between topics to prevent prompt poisoning.

## Why?
メッチャケチだからな. If you want a fully automated process, point your paid subscription LLM to this repo and tell it to "make this but fully automated using you". Et Voilà!