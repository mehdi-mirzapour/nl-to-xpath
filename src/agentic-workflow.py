import json
import re
from pathlib import Path
from typing import Dict, Optional
from playwright.sync_api import sync_playwright
from llm_xpath import process_instruction_with_html

import asyncio
from rag_html_mistral_pinecone import process_and_query_html  # Assuming the function is in rag_processor.py

def sync_call_html_context_findre(html_content, query, top_k=1):
    """Synchronous function that calls the async process_and_query_html."""
    try:
        # Call the async function using asyncio.run
        result = asyncio.run(process_and_query_html(html_content, query, top_k))
        if result:
            print("\nQuery result:")
            print(f"Chunk: {result['text'][:200]}...")  # Truncate for display
            print(f"Source: {result['source']}")
            print(f"Offsets: {result['start_offset']} - {result['end_offset']}")
            print(f"Score: {result['score']}")
        return result['text']
    except Exception as e:
        print(f"Error in sync_call_html_processor: {e}")
        return None
    
    
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


            if classification == "page.fill":
                print(instruction_text)
                result = process_instruction_with_html(instruction_text, page.content())
                print(result)
                page.locator(result["xpath"]).fill(result["fill"])
                
            if classification  == "page.click":
                print(instruction_text)
                result = process_instruction_with_html(instruction_text, page.content())
                print(result)
                page.locator(result["xpath"]).click()
                
            if classification in {"page.wait"}:
                page.wait_for_timeout(waiting_time*1000)
                
            if classification in {"browser.close"}:
                browser.close()

            if classification == "page.goto":
                url = extract_url(instruction_text)
                print(url)
                page.goto(url)

            



if __name__ == "__main__":
    main()
