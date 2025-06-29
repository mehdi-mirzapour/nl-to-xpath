import json
import re
from pathlib import Path
from typing import Dict, Optional

import nest_asyncio
nest_asyncio.apply()

import asyncio
from playwright.sync_api import sync_playwright
from llm_xpath import process_instruction_with_html
from rag_html_mistral_pinecone import process_and_query_html  # Assuming the function is in rag_processor.py

INPUT_PATH = Path("resources/docs/classifier.json")

def extract_url(text: str) -> Optional[str]:
    """
    Extract the first URL found in the input text.
    """
    pattern = r'https?://[^\s")]+'
    match = re.search(pattern, text)
    return match.group(0) if match else None

async def async_call_html_context_findre(html_content, query, top_k=1):
    try:
        result = await process_and_query_html(html_content, query, top_k)
        if result:
            print("\nQuery result:")
            print(f"Chunk: {result['text'][:200]}...")
            print(f"Source: {result['source']}")
            print(f"Offsets: {result['start_offset']} - {result['end_offset']}")
            print(f"Score: {result['score']}")
        return result['text']
    except Exception as e:
        print(f"Error in async_call_html_context_findre: {e}")
        return None

def run_async_blocking(coro):
    """
    Run an async coroutine inside a sync function, handling nested event loops.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    else:
        return loop.run_until_complete(coro)

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
                small_html_context = run_async_blocking(async_call_html_context_findre(html, query=instruction_text))
                result = process_instruction_with_html(instruction_text, small_html_context)
                print(f"Filling field at XPath {result['xpath']} with value '{result['fill']}'")
                page.locator(result["xpath"]).fill(result["fill"])

            elif classification == "page.click":
                print(f"Instruction: {instruction_text}")
                html = page.content()
                small_html_context = run_async_blocking(async_call_html_context_findre(html, query=instruction_text))
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
