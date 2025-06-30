from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("http://localhost:5173")
    page.wait_for_timeout(5 * 1000)  # 5 minutes = 300000 ms

