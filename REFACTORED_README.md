# NL-to-XPath Live Visualization

A beautiful web interface for visualizing natural language to XPath automation in real-time.

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
│       ├── demo.txt    # Demo test case
│       └── 1.txt       # Original test case
├── tests/              # Test files
├── .env                # Environment variables (API keys)
├── requirements.txt    # Python dependencies
└── venv/              # Virtual environment

## 🚀 Quick Start

### 1. Install Dependencies
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install
```

### 2. Configure API Keys
Edit `.env` and add your API keys:
```
OPENAI_API_KEY=your_key_here
MISTRAL_API_KEY=your_key_here
PINECONE_API_KEY=your_key_here
```

### 3. Run the Server
```bash
venv/bin/uvicorn backend.server:app --reload --port 8000
```

### 4. Open Browser
Navigate to `http://localhost:8000` and click **"Start Demo"**

## ✨ Features

- 🎨 **Beautiful Modern UI** with gradient backgrounds and glassmorphism
- ⚡ **Real-time Updates** via WebSocket streaming
- 🖼️ **Live Screenshots** showing agent execution
- 📝 **Instruction Highlighting** showing current step
- 🎯 **Smart XPath Extraction** using LLMs
- 🌐 **Works with Any Website** (demo uses SauceDemo)

## 🛠️ Technology Stack

**Backend:**
- FastAPI (Web framework)
- Playwright (Browser automation)
- LangChain (LLM integration)
- OpenAI GPT-4o-mini (Natural language processing)

**Frontend:**
- Pure HTML/CSS/JavaScript
- WebSocket for real-time communication
- Modern glassmorphism design
- Inter font for beautiful typography

## 📝 License

MIT License - see LICENSE file for details
