from http.server import HTTPServer, BaseHTTPRequestHandler

class StaticHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Send the same response for any path
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"Blocked by LliureX-Guard\n")

    def do_POST(self):
        # Handle POST requests with the same static response
        self.do_GET()

if __name__ == "__main__":
    # Bind to 127.0.80.80 (localhost) on port 8080
    server_address = ("127.0.80.80", 8080)
    httpd = HTTPServer(server_address, StaticHandler)
    print(f"Serving on http://127.0.80.80:8080")
    httpd.serve_forever()

