from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    page.goto('https://www.saucedemo.com/')
    page.locator("//input[@id='user-name']").fill('standard_user')
    page.locator("//input[@id='password']").fill('secret_sauce')
    page.locator("//input[@id='login-button']").click()
    page.wait_for_timeout(5000)
    page.wait_for_timeout(3000)
    browser.close()