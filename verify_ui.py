import subprocess
import time
from playwright.sync_api import sync_playwright

# Start a local HTTP server in the background
# The files don't have .html extension, so we need a custom handler to force text/html
custom_server_script = """
import http.server
import socketserver

PORT = 8001

class Handler(http.server.SimpleHTTPRequestHandler):
    def guess_type(self, path):
        # Force text/html for our specific files without extensions
        if path.endswith('/bloque_1') or path.endswith('/bloque_2') or path.endswith('/bloque_4'):
            return 'text/html'
        return super().guess_type(path)

socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    httpd.serve_forever()
"""

with open("custom_server.py", "w") as f:
    f.write(custom_server_script)

server_process = subprocess.Popen(['python3', 'custom_server.py'])

# Wait for the server to start
time.sleep(2)

try:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Capture bloque_1
        page.goto('http://localhost:8001/bloque_1', wait_until='domcontentloaded')
        page.screenshot(path='screenshot_bloque_1.png', full_page=True)

        # Capture bloque_2
        page.goto('http://localhost:8001/bloque_2', wait_until='domcontentloaded')
        page.screenshot(path='screenshot_bloque_2.png', full_page=True)

        # Capture bloque_4
        page.goto('http://localhost:8001/bloque_4', wait_until='domcontentloaded')
        page.screenshot(path='screenshot_bloque_4.png', full_page=True)

        browser.close()
finally:
    # Stop the local HTTP server
    server_process.terminate()
