from playwright.sync_api import sync_playwright

def capture_screenshot():
    with sync_playwright() as p:
        browser = p.chromium.launch(args=['--no-sandbox'])
        page = browser.new_page(viewport={"width": 1280, "height": 1024})
        # Load the HTML file
        page.goto('file:///app/general.html')
        # Wait a moment for rendering
        page.wait_for_timeout(2000)
        # Take full page screenshot
        page.screenshot(path='screenshot.png', full_page=True)
        browser.close()

if __name__ == "__main__":
    capture_screenshot()
