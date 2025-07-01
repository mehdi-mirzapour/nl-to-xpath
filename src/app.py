import json
import logging
import threading
import time
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from rich.logging import RichHandler
from playwright.sync_api import sync_playwright

# Your custom modules (placeholders here)
from models import model
from segmentor import segment
from classifier import classify
from extractor import extract_xpath_pattern
from utils import load_instructions_from_file, extract_url

# ------------------------
# Logging Setup
# ------------------------
log_stream = []
class UILogHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        log_stream.append(log_entry)

formatter = logging.Formatter("%(message)s")
ui_handler = UILogHandler()
ui_handler.setFormatter(formatter)

logging.basicConfig(
    level=logging.INFO,
    handlers=[RichHandler(markup=True), ui_handler]
)
log = logging.getLogger("rich")

# ------------------------
# FastAPI App Setup
# ------------------------
app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "logs": log_stream})

@app.post("/run", response_class=HTMLResponse)
def run_instruction(request: Request, instruction: str = Form(...)):
    def automation_thread():
        log.info(f"📥 Instruction: {instruction}")
        segmented = segment(instruction, model)
        classified = classify(segmented, model)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()

            for item in classified.get("instructions", []):
                classification = item.get("classification")
                instruction_text = item.get("original instruction")
                waiting_time = item.get("waiting_time", 2)

                log.info(f"📝 Instruction: {instruction_text}")
                log.info(f"📝 Class: {classification}")

                if classification == "page.goto":
                    url = extract_url(instruction_text)
                    log.info(f"🌐 Navigating to: {url}")
                    page.goto(url)

                elif classification == "page.fill":
                    html = page.content()
                    result = extract_xpath_pattern(instruction_text, html, model)
                    log.info(f"🔢 Filling: {result['xpath']} with {result['fill']}")
                    page.locator(result["xpath"]).fill(result["fill"])

                elif classification == "page.click":
                    html = page.content()
                    result = extract_xpath_pattern(instruction_text, html, model)
                    log.info(f"🔘 Clicking: {result['xpath']}")
                    page.locator(result["xpath"]).click()

                elif classification == "page.wait":
                    log.info(f"⏳ Waiting: {waiting_time} seconds")
                    page.wait_for_timeout(waiting_time * 1000)

                elif classification == "browser.close":
                    log.info("👋 Closing browser...")
                    browser.close()

                page.wait_for_timeout(1000)

    thread = threading.Thread(target=automation_thread)
    thread.start()

    return templates.TemplateResponse("index.html", {"request": request, "logs": log_stream})
