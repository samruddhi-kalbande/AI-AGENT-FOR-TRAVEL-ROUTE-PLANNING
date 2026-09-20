# Deployment Guide: Atlas AI Travel Route Planning Agent

This guide explains how to deploy the **Atlas AI Travel Route Planning Agent** to modern cloud platforms including **Render**, **Docker**, **Hugging Face Spaces**, and **Railway**.

---

## 📋 Architecture Considerations

Atlas consists of:
1. **FastAPI Backend (Python 3.11+)**: Serves REST APIs and executes the LangChain agent.
2. **React Web App (Node.js / Static SPA)**: Modern Vite-built single-page application.
3. **Gradio Conversational UI (Python)**: Standalone or integrated interactive chat interface.

---

## 🐳 Option 1: Docker (Single Container Full-Stack)

You can containerize and run the entire application using the included `Dockerfile`.

### Build & Run:
```bash
docker build -t atlas-travel-agent .
docker run -p 8000:8000 -p 7860:7860 -e GROQ_API_KEY="gsk_..." -e TAVILY_API_KEY="tvly-..." atlas-travel-agent
```

---

## 🚀 Option 2: Render Deployment (`render.yaml`)

Atlas includes a production-ready `render.yaml` blueprint.

1. Fork or push this repository to your GitHub account.
2. Log into [Render.com](https://render.com).
3. Click **New +** → **Blueprint**.
4. Connect this repository: Render will automatically detect `render.yaml` and provision:
   - Web Service: FastAPI Backend + Gradio
   - Static Site: Vite React Frontend
5. Add your `GROQ_API_KEY` and `TAVILY_API_KEY` in the Render dashboard environment variables.

---

## 🤗 Option 3: Hugging Face Spaces (Gradio & Full Backend)

1. Create a new Space on [Hugging Face](https://huggingface.co/spaces) with SDK: **Docker** or **Gradio**.
2. Push the repository contents to your Space.
3. Set `GROQ_API_KEY` and `TAVILY_API_KEY` in the Space **Settings** → **Variables and secrets**.
4. The conversational agent and API will boot automatically.

---

## 💻 Local Quick Launch

### Windows (1-Click):
Double-click `run.bat` or execute in PowerShell:
```cmd
run.bat
```

### Linux / macOS (1-Click):
```bash
chmod +x run.sh
./run.sh
```
