# BharatGPT
**Chatbot-offline version – with audio, PDF, text and image input support!**

## What is BharatGPT?
BharatGPT is an offline AI chatbot that works like ChatGPT but runs completely on your device.
It does not require a server or external API for chat, transcription, PDF retrieval, or image understanding.

## Features
- **Chat offline** using a local GGUF LLM
- **Talk with voice** using microphone input
- **Upload audio** for transcription
- **Ask questions from PDFs**
- **Text-based Q&A**
- **Image understanding** with a matching LLaVA model
- **Private by design** – data stays on your system
- **No runtime model downloads**

## Tech Stack
- Python
- Streamlit
- LLaMA/LLaVA GGUF models
- Whisper for speech-to-text
- PyMuPDF-compatible PDF text extraction through pypdfium2
- Transformers and PyTorch for embeddings
- ChromaDB for local PDF retrieval

## Installation and Run
```bash
python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# Windows Command Prompt:
# .venv\Scripts\activate.bat
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

The project disables Streamlit's file watcher in `.streamlit/config.toml` to avoid a
PyTorch `torch.classes` inspection error on Windows. Restart the app manually after
changing code.

Model files are not included in the repository. Place existing local model files in:

```text
models/
  llava/
    ggml-model-q4_k.gguf
    mmproj-model-f16.gguf
  bge-large-en-v1.5/
    model.safetensors
    config.json
    modules.json
    1_Pooling/config.json
    ...tokenizer files
  whisper-small/
    model.safetensors
    config.json
    preprocessor_config.json
    ...tokenizer files
```

The LLaVA GGUF is used for text and image questions; image understanding also requires
the matching `mmproj-model-f16.gguf` projector. The project pins `llama-cpp-python`
to version 0.2.90 for compatibility with this canonical LLaVA 1.5 pair. The text GGUF
and mmproj must belong to the same vision model. The BGE and Whisper folders should
contain their complete local model files. Model loading is local-only; the app does not
download models at runtime. Whisper-small was found in the Windows Hugging Face cache
for this setup and copied into `models/whisper-small`.

Chroma telemetry is disabled. Local chat avatars are built into the app and do not load
images from external websites.

## Requirements
```bash
python -m pip install -r requirements.txt
```

## Why BharatGPT?
Not everyone wants to send their data to the cloud. BharatGPT gives you full control
over your AI chatbot – in your language, on your terms.