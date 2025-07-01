import json
import logging
from models import model
from segmentor import segment
from classifier import classify
from extractor import extract_xpath_pattern
from playwright.sync_api import sync_playwright
from rag import process_html_query 
from rich.logging import RichHandler
import logging
from utils import *

# ------------------------
# Setup Logging with Emojis
# ------------------------
logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(markup=True)]
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
log.info(f"📦 User Input as JSON:\n{json.dumps(user_data, indent=2)}")

# Convert NL to structured instructions
output = segment(instruction, model)
log.info("📤 Segmentor Output:\n" + str(output))

# Classify the instructions
output = classify(output, model)
log.info("📤 Classifier Output:\n" + str(output))


# Save to JSON file
with open("resources/docs/classification.json", "w") as f:
    json.dump(output, f, indent=4)
    
with open("resources/docs/classification.json", "r") as f:
    out = json.load(f)

log.info("📤 Classifier Output:\n" + str(output))

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    
    for item in output.get("instructions", []):
        classification = item.get("classification")
        instruction_text = item.get("original instruction")
        waiting_time = item.get("waiting_time")
        
        log.info(f"📝 Instruction: {instruction_text}")
        log.info(f"📝 Class: {classification}")
        log.info(f"📝 Waiting_time: {waiting_time}")

        if classification == "page.goto":
            url = extract_url(instruction_text)
            log.info(f"🌐 Navigating to: {url}")
            page.goto(url)

        elif classification == "page.fill":
            html = page.content()
            result = extract_xpath_pattern(instruction_text, html, model)
            log.info(f"🔢 Filling field at XPath `{result['xpath']}` with value `{result['fill']}`")
            page.locator(result["xpath"]).fill(result["fill"])

        elif classification == "page.click":
            html = page.content()
            result = extract_xpath_pattern(instruction_text, html, model)
            log.info(f"🔢 Clicking field at XPath `{result['xpath']}`")
            page.locator(result["xpath"]).click()
            page.wait_for_timeout(5000) # wait for 5 seconds to let the page loads

        elif classification == "page.wait":
            log.info(f"⏳ Waiting for {waiting_time} seconds...")
            page.wait_for_timeout(waiting_time * 1000)

        elif classification == "browser.close":
            log.info("👋 Closing browser...")
            browser.close()
                

            
        