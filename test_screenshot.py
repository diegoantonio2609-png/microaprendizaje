import sys
from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto('file:///app/bloque_2')
        page.screenshot(path='bloque_2_updated_screenshot.png', full_page=True)
        browser.close()

if __name__ == '__main__':
    main()
