import json
import logging
from models import model
from sentence_segmentor import segment
from task_mapper import classify
from xpath_extractor import extract_xpath_pattern
from playwright.sync_api import sync_playwright
from rag_html import process_html_query 
from rich.logging import RichHandler
from utils import *
from pprint import pformat


# ------------------------
# Setup Logging with Emojis
# ------------------------
logging.basicConfig(
    level="INFO",
    format="%(message)s",
    handlers=[RichHandler(markup=True, rich_tracebacks=True)]
)
log = logging.getLogger("rich")


instruction = """
open localhost:5173 and then login with user name as `mehdi.mirzapour@gmail.com` and password  as `pass1234`
open localhost:5173/items .
click on add items and then fill out the Title with "Meeting Agenda" and then the Description as "Topics to Discuss". click on save buttom.
click on the add items and enter the Title as "Event Name" and the Description as "Event Details". click on save buttom.
exit the browser.
"""

# Wrap input in JSON structure
user_data = {"user_inputs": instruction.strip()}
log.info(f"🗃️  User Input as JSON:\n{json.dumps(user_data, indent=2)}")

# Convert NL to structured instructions
output = segment(instruction, model)
log.info("🧩 Sentence Segmentor Output:\n" + str(output))

# Classify the instructions
output = classify(output, model)
log.info("🧠 Task Mapper Output:\n" + str(output))

# Save to JSON file
with open("resources/docs/classification.json", "w") as f:
    json.dump(output, f, indent=4)

with open("resources/docs/classification.json", "r") as f:
    out = json.load(f)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    for item in output.get("instructions", []):
        classification = item.get("classification")
        instruction_text = item.get("original instruction")
        waiting_time = item.get("waiting_time")

        log.info(f"✏️ Instruction: {instruction_text}")
        log.info(f"🏷️ Class: {classification}")
        log.info(f"⏱️ Waiting_time: {waiting_time}")

        if classification == "page.goto":
            url = extract_url(instruction_text)
            log.info(f"🌍 Navigating to: {url}")
            page.goto(url)

        elif classification == "page.fill":
            html = page.content()
            result = extract_xpath_pattern(instruction_text, html, model)
            
            prefix_spaces = " " * 30

            print(f"{prefix_spaces}🖨️  Extracted XPath result (print):")
            for key, value in result.items():
                print(f"{prefix_spaces}   {key}: {value}")
            
            page.locator(result["xpath"]).fill(result["fill"])

        elif classification == "page.click":
            html = page.content()
            result = extract_xpath_pattern(instruction_text, html, model)
            
            prefix_spaces = " " * 30

            print(f"{prefix_spaces}🖨️  Extracted XPath result (print):")
            for key, value in result.items():
                print(f"{prefix_spaces}   {key}: {value}")

                
            page.locator(result["xpath"]).click()
            page.wait_for_timeout(5000)

        elif classification == "page.wait":
            log.info(f"⏳ Waiting for {waiting_time} seconds...")
            if waiting_time is None:
                waiting_time = 5
            page.wait_for_timeout(waiting_time * 1000)

        elif classification == "browser.close":
            log.info("🚪 Closing browser...")
            browser.close()
