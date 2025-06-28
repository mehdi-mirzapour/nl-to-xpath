from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    # Step 1: Go to the website
    page.goto("https://app.thundercode.ai")

    # Step 2: Fill the username field using XPath
    page.locator("//input[@id='username']").fill("mehdi@proptexx.com")

    # Step 3: Fill the password field using XPath
    page.locator("//input[@id='password']").fill("9X4RKrkr9p5e3DH")

    # Step 4: Click the "Continue" button (based on visible text)
    page.locator("//button[contains(text(), 'Continue')]").click()
    
    # # Step 5: Fill the URL field
    # page.locator("//input[@id='url']").fill("https://kankosh.com/")
    
    # # Step 6: Click the "Next" button
    # page.locator("//button[span[text()='Next']]").click()
    # Wait explicitly for 5 seconds (if nothing else to wait on)
    
    page.wait_for_timeout(5000)
    page.goto("https://app.thundercode.ai/#/organization/overview")
    # page.locator("//div[text()='Products and services']").click()
    # page.wait_for_timeout(10000)
    # page.locator("//div[text()='Quality practices']").click()

    page.locator("//input[@id='founded']").fill("2029")
    page.locator("//span[text()='Save']/ancestor::button").click()

    page.wait_for_timeout(5000)
    page.goto("https://app.thundercode.ai/#/organization/quality-practices")
    page.locator("//input[@id='otherStandards']").fill("ISO 9001, ISO 27002")
    page.locator("//span[text()='Save']/ancestor::button").click()

    # Optional: wait to observe the result
    page.wait_for_timeout(1000)

    browser.close()
