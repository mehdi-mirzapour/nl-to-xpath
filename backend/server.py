from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import json
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from agentic_app import run_agent

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve index.html at root
@app.get("/")
async def read_root():
    frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
    return FileResponse(frontend_path)

class InstructionResponse(BaseModel):
    content: str

@app.get("/instructions", response_model=InstructionResponse)
async def get_instructions():
    demo_path = os.path.join(os.path.dirname(__file__), "..", "resources", "test_cases", "demo.txt")
    with open(demo_path, "r") as f:
        content = f.read()
    return {"content": content}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    try:
        # Wait for a start message
        data = await websocket.receive_text()
        if data == "start":
            # Read instructions
            demo_path = os.path.join(os.path.dirname(__file__), "..", "resources", "test_cases", "demo.txt")
            with open(demo_path, "r") as f:
                instruction_text = f.read().strip()
            
            # Use a queue to communicate between sync and async contexts
            import queue
            message_queue = queue.Queue()
            
            # Callback to send updates to WebSocket
            def update_callback(step_data):
                message_queue.put(step_data)

            # Run agent in a separate thread
            import threading
            agent_thread = threading.Thread(
                target=run_agent, 
                args=(instruction_text, update_callback)
            )
            agent_thread.start()
            
            # Process messages from queue and send via WebSocket
            while agent_thread.is_alive() or not message_queue.empty():
                try:
                    # Non-blocking get with timeout
                    step_data = message_queue.get(timeout=0.1)
                    await websocket.send_json(step_data)
                except queue.Empty:
                    # Allow other async tasks to run
                    await asyncio.sleep(0.1)
            
            # Wait for thread to complete
            agent_thread.join()
            
            await websocket.send_json({"status": "complete"})
            
    except Exception as e:
        print(f"WebSocket error: {e}")
        import traceback
        traceback.print_exc()
        await websocket.close()

