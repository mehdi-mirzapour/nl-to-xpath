# NL-to-XPath Live Visualization

A beautiful web interface for visualizing natural language to XPath automation in real-time. This project transforms natural language commands (e.g., *"Click on 'About Us'"*) into precise XPath expressions and executes them with live visual feedback.

---

## ✨ Features

- 🎨 **Beautiful Modern UI** with gradient backgrounds and glassmorphism effects
- ⚡ **Real-time Updates** via WebSocket streaming
- 🖼️ **Live Screenshots** showing agent execution step-by-step
- 📝 **Instruction Highlighting** showing current step progress
- 🎯 **Smart XPath Extraction** using LLMs (OpenAI GPT-4o-mini)
- 🌐 **Works with Any Website** (demo uses SauceDemo)
- 🤖 **AI-Powered** using LangChain and OpenAI models

---

## 📁 Project Structure

```
xpath/
├── backend/              # Python backend code
│   ├── server.py        # FastAPI server with WebSocket
│   ├── agentic_app.py   # Main agent logic
│   ├── models.py        # LLM model configuration
│   ├── xpath_extractor.py
│   ├── sentence_segmentor.py
│   ├── task_mapper.py
│   └── ...
├── frontend/            # Web frontend
│   └── index.html      # Beautiful UI with live updates
├── resources/           # Test cases and data
│   └── test_cases/
│       ├── demo.txt    # Demo test case (SauceDemo)
│       └── 1.txt       # Original test case
├── tests/              # Test files
├── .env                # Environment variables (API keys)
├── requirements.txt    # Python dependencies
└── venv/              # Virtual environment
```

---

## 🚀 Quick Start

### 1. Create and Activate Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
.\venv\Scripts\activate   # Windows
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
playwright install
```

### 3. Configure API Keys

Create a `.env` file in the root directory:

```env
MAX_TOKEN_LIMITATION=128000

OPENAI_API_KEY=sk-your-real-openai-api-key-here
MISTRAL_API_KEY=your-real-mistral-api-key-here

PINECONE_API_KEY=your-real-pinecone-api-key-here
PINECONE_INDEX_NAME=thundercode
```

> **Important:**  
> - Replace the placeholder values with your actual API keys  
> - Keep this file **private** and **do not** commit it to any public repository

### 4. Run the Server

```bash
venv/bin/uvicorn backend.server:app --reload --port 8000
```

### 5. Open Browser

Navigate to **`http://localhost:8000`** and click **"▶ Start Demo"**

---

## 🎯 Usage

### Web Interface (Recommended)

1. Start the server (see step 4 above)
2. Open `http://localhost:8000` in your browser
3. Click "Start Demo" to watch the agent execute the test case
4. See real-time updates with live screenshots

### Command Line

Run the agent directly from the command line:

```bash
venv/bin/python backend/agentic_app.py resources/test_cases/demo.txt
```

This will execute the test case and save the generated Playwright script to `resources/test_cases/demo.py`.

---

## 🛠️ Technology Stack

**Backend:**
- FastAPI (Web framework)
- Playwright (Browser automation)
- LangChain (LLM integration)
- OpenAI GPT-4o-mini (Natural language processing)
- WebSocket (Real-time communication)

**Frontend:**
- Pure HTML/CSS/JavaScript
- Modern glassmorphism design
- Inter font for beautiful typography
- WebSocket client for live updates

---

## 📝 Notes

- Tested on Python 3.9.6, but Python 3.11+ is recommended
- Ensure your API keys have the proper permissions
- The demo test case uses [SauceDemo](https://www.saucedemo.com/) for testing
- Original test cases require the [`full-stack-fastapi-template`](https://github.com/fastapi/full-stack-fastapi-template.git) running locally

---

## 🤝 Contributing & Issues

If you encounter any issues or want to contribute, please open an issue or submit a pull request!

---

**Thank you for using NL-to-XPath Live Visualization!** 🚀