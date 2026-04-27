from playwright.sync_api import sync_playwright

def verify():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto('http://localhost:8001/bloque_2', wait_until='domcontentloaded')

        # Take initial screenshot
        page.screenshot(path='screenshot_bloque_2_initial.png', full_page=True)

        # Click the accordion to open it
        page.click('#privacy-accordion-toggle')

        # Wait a bit for the animation to finish
        page.wait_for_timeout(500)

        # Take screenshot after click
        page.screenshot(path='screenshot_bloque_2_opened.png', full_page=True)

        browser.close()
        print("Screenshots taken successfully.")

if __name__ == '__main__':
    verify()
