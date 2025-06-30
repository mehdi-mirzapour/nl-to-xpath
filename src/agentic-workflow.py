import json
import re
import logging
from pathlib import Path
from typing import Dict, Optional
from model_llm import model
from llm_nl_to_instruct import nl_to_instruct
from playwright.sync_api import sync_playwright
from llm_xpath import process_instruction_with_html
from rag_html_mistral_pinecone import process_html_query 

INPUT_PATH = Path("resources/docs/classifier.json")

# ------------------------
# Setup Logging with Emojis
# ------------------------
from rich.logging import RichHandler
import logging

logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(markup=True)]
)
log = logging.getLogger("rich")



def extract_url(text: str) -> Optional[str]:
    pattern = r'https?://[^\s")]+'
    match = re.search(pattern, text)
    return match.group(0) if match else None


def main():
    with INPUT_PATH.open("r") as f:
        data = json.load(f)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        for item in data.get("instructions", []):
            classification = item.get("classification")
            instruction_text = item.get("original instruction")
            waiting_time = item.get("waiting_time")

            if classification == "page.goto":
                url = extract_url(instruction_text)
                log.info(f"🌐 Navigating to: {url}")
                page.goto(url)

            elif classification == "page.fill":
                log.info(f"📝 Instruction: {instruction_text}")
                html = page.content()
                small_html_context = process_html_query(html, query=instruction_text)
                result = process_instruction_with_html(instruction_text, small_html_context)
                log.info(f"🔢 Filling field at XPath `{result['xpath']}` with value `{result['fill']}`")
                page.locator(result["xpath"]).fill(result["fill"])

            elif classification == "page.click":
                log.info(f"🖱️ Instruction: {instruction_text}")
                html = page.content()
                small_html_context = process_html_query(html, query=instruction_text)
                result = process_instruction_with_html(instruction_text, small_html_context)
                log.info(f"👆 Clicking element at XPath `{result['xpath']}`")
                page.locator(result["xpath"]).click()

            elif classification == "page.wait":
                log.info(f"⏳ Waiting for {waiting_time} seconds...")
                page.wait_for_timeout(waiting_time * 1000)

            elif classification == "browser.close":
                log.info("👋 Closing browser...")
                browser.close()


if __name__ == "__main__":
    instruction = """
open localhost:5173 and then login with user name as `mehdi.mirzapour@gmail.com` and password  as `pass1234`
open localhost:5173/items and click on add items.
"""
    # Wrap input in JSON structure
    user_data = {"user_inputs": instruction.strip()}
    log.info(f"📦 User Input as JSON:\n{json.dumps(user_data, indent=2)}")

    # Convert NL to structured instructions
    output = nl_to_instruct(instruction, model)

    # 🪄 Log outputs
    log.info("📤 Step-by-step Output:\n" + output.strip())

