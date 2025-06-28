import json
import re
from pathlib import Path
from typing import Dict, Optional
from playwright.sync_api import sync_playwright

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


            if classification in {"page.fill", "page.click"}:
                # result = get_xpath_and_html(instruction_text)
                # print(result)
                pass
                
            if classification in {"page.wait"}:
                # item["waiting_time"]
                pass
                
            if classification in {"browser.close"}:
                pass

            elif classification == "page.goto":
                url = extract_url(instruction_text)
                print(url)
                page.goto(url)



if __name__ == "__main__":
    main()
