# AICO: AI Coder

AICO is a command-line coding assistant.
It works through OpenAI / Anthropic / Google LLM API or directly using PyTorch for inference.

## ✨ Installation

**Requirements:**  
- Python **3.11+** (tested on Linux, Windows, Mac)

**Clone & Install dependencies:**

```sh
git clone https://github.com/Nayjest/aico.git
cd aico
pip install -r requirements/prod.txt
```

**(Optional: Development/Testing tools)**

```sh
pip install -r requirements/dev.txt
```

---

## ⚙️ Configuration

AICO reads settings from a `.env` file at launch — **you must provide an LLM API key**.

1. **Copy & edit** `.env`:
    ```sh
    cp .env.example .env
    ```
    Or just create your own `.env` (see sample below).

2. **Edit your `.env` file:**
    ```
    # For OpenAI API
    LLM_API_KEY=sk-...
    MODEL=gpt-4.1
    ```

## 🛠️ Usage



## 🧑‍💻 Development

Contributions very welcome!  
- [ ] Fork & PR, or contact [Vitalii Stepanenko](mailto:mail@vitaliy.in)
- [ ] To publish: see the `Makefile` for build/test commands
- [ ] Tests live in [`tests/`](./tests/)

---

## 📜 License

Licensed under the [MIT License](https://github.com/Nayjest/aico/blob/main/LICENSE)  
© 2023–2025 [Vitalii Stepanenko](mailto:mail@vitaliy.in)