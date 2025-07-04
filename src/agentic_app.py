import argparse
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
import os

# ------------------------
# Setup Logging with Emojis
# ------------------------
logging.basicConfig(
    level="INFO",
    format="%(message)s",
    handlers=[RichHandler(markup=True, rich_tracebacks=True)]
)
log = logging.getLogger("rich")

# ------------------------
# Parse command-line argument for instruction file
# ------------------------
parser = argparse.ArgumentParser(description="Run browser instructions from a file.")
parser.add_argument("instruction_file", help="Path to the instruction text file.")
args = parser.parse_args()

# ------------------------
# Read instructions from file
# ------------------------
with open(args.instruction_file, "r") as f:
    instruction = f.read().strip()

# Wrap input in JSON structure
user_data = {"user_inputs": instruction}
log.info(f"🗃️  User Input as JSON:\n{json.dumps(user_data, indent=2)}")

# Convert NL to structured instructions
output = segment(instruction, model)
log.info("🧩 Sentence Segmentor Output:\n" + str(output))

# Classify the instructions
output = classify(output, model)
log.info("🧠 Task Mapper Output:\n" + str(output))

# Save to JSON file (same name as input but .json extension)
json_path = args.instruction_file.rsplit('.', 1)[0] + ".json"
with open(json_path, "w") as f:
    json.dump(output, f, indent=4)

with open(json_path, "r") as f:
    out = json.load(f)

page_commands = [
    "from playwright.sync_api import sync_playwright",
    "",
    "with sync_playwright() as p:",
    "    browser = p.chromium.launch(headless=False)",
    "    page = browser.new_page()",
    ""
]

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
            page_commands.append(f"    page.goto({repr(url)})")

        elif classification == "page.fill":
            html = page.content()
            result = extract_xpath_pattern(instruction_text, html, model)
            print(" " * 30 + "🖨️  Extracted XPath result (print):")
            for key, value in result.items():
                print(" " * 30 + f"{key}: {value}")
            page.locator(result["xpath"]).fill(result["fill"])
            page_commands.append(f'    page.locator({repr(result["xpath"])}).fill({repr(result["fill"])})')

        elif classification == "page.click":
            html = page.content()
            result = extract_xpath_pattern(instruction_text, html, model)
            print(" " * 30 + "🖨️  Extracted XPath result (print):")
            for key, value in result.items():
                print(" " * 30 + f"{key}: {value}")
            page.locator(result["xpath"]).click()
            page.wait_for_timeout(5000)
            page_commands.append(f'    page.locator({repr(result["xpath"])}).click()')
            page_commands.append(f"    page.wait_for_timeout(5000)")

        elif classification == "page.hover":
            html = page.content()
            result = extract_xpath_pattern(instruction_text, html, model)
            print(" " * 30 + "🖨️  Extracted XPath result (print):")
            for key, value in result.items():
                print(" " * 30 + f"{key}: {value}")
            xpath = result["xpath"]
            # Wait for element to ensure it's present and visible
            page.wait_for_selector(xpath, state='visible', timeout=10000)
            element = page.locator(xpath)
            
            # Verify element is visible
            if not element.is_visible():
                print("Error: Element is not visible!")
                browser.close()
                exit()
            
            # Add temporary CSS to highlight the element on click
            page.evaluate(
                """() => {
                    const style = document.createElement('style');
                    style.innerHTML = 'th:active, th:focus { background-color: yellow !important; outline: 2px solid blue !important; }';
                    document.head.appendChild(style);
                }"""
            )
            
            # Get bounding box for explicit mouse movement
            bounding_box = element.bounding_box()
            if bounding_box:
                x = bounding_box['x'] + bounding_box['width'] / 2
                y = bounding_box['y'] + bounding_box['height'] / 2
                print(" " * 30 + f"Moving mouse to: ({x}, {y})")
                page.mouse.move(x, y)  # Explicit mouse movement for visibility
                # Perform click to select the element
                element.click()
                # Capture screenshot to verify
                png_path = args.instruction_file.rsplit('.', 1)[0] + ".png"
                page.screenshot(path=png_path)
                # Add delay to observe effect
                page.wait_for_timeout(3000)
            
            page_commands.append(f'    page.locator({repr(result["xpath"])}).hover()')
            page_commands.append(f"    page.wait_for_timeout(5000)")

        elif classification == "page.wait":
            log.info(f"⏳ Waiting for {waiting_time} seconds...")
            if waiting_time is None:
                waiting_time = 5
            page.wait_for_timeout(waiting_time * 1000)
            page_commands.append(f"    page.wait_for_timeout({waiting_time * 1000})")

        elif classification == "browser.close":
            log.info("🚪 Closing browser...")
            browser.close()
            page_commands.append("    browser.close()")

# Add final line to close browser context if not closed explicitly
if not any("browser.close()" in cmd for cmd in page_commands):
    page_commands.append("    browser.close()")

# Save page commands as .py file with same base name as input
py_path = args.instruction_file.rsplit('.', 1)[0] + ".py"
with open(py_path, "w") as f:
    f.write("\n".join(page_commands))

log.info(f"💾 Saved browser commands to {py_path}")
