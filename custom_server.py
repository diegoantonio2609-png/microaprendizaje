
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
