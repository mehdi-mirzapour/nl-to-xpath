import json
import re
from pathlib import Path
from typing import Dict, Optional

from playwright.sync_api import sync_playwright
from llm_xpath import process_instruction_with_html
from rag_html_mistral_pinecone import process_and_query_html 

INPUT_PATH = Path("resources/docs/classifier.json")

def extract_url(text: str) -> Optional[str]:
    """
    Extract the first URL found in the input text.
    """
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
                print(f"Navigating to: {url}")
                page.goto(url)

            elif classification == "page.fill":
                print(f"Instruction: {instruction_text}")
                html = page.content()
                small_html_context = process_and_query_html(html, query=instruction_text)
                result = process_instruction_with_html(instruction_text, small_html_context)
                print(f"Filling field at XPath {result['xpath']} with value '{result['fill']}'")
                page.locator(result["xpath"]).fill(result["fill"])

            elif classification == "page.click":
                print(f"Instruction: {instruction_text}")
                html = page.content()
                small_html_context = process_and_query_html(html, query=instruction_text)
                result = process_instruction_with_html(instruction_text, small_html_context)
                print(f"Clicking element at XPath {result['xpath']}")
                page.locator(result["xpath"]).click()

            elif classification == "page.wait":
                print(f"Waiting for {waiting_time} seconds...")
                page.wait_for_timeout(waiting_time * 1000)

            elif classification == "browser.close":
                print("Closing browser...")
                browser.close()

if __name__ == "__main__":
    main()
