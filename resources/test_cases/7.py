from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    page.goto('localhost:5173')
    page.wait_for_timeout(5000)
    page.locator("//input[@id='username']").fill('mehdi.mirzapour@gmail.com')
    page.locator("//input[@name='password']").fill('pass1234')
    page.locator("//button[contains(text(), 'Log In')]").click()
    page.wait_for_timeout(5000)
    page.goto('localhost:5173/items')
    page.locator("//button[@value='add-item']").click()
    page.wait_for_timeout(5000)
    page.locator("//input[@id='title']").fill('Client Notes')
    page.locator("//input[@id='description']").fill('Discussion points from client meeting')
    page.locator("//button[@type='submit']").click()
    page.wait_for_timeout(5000)
    browser.close()