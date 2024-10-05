import http.server
import socketserver
import markdown2

PORT = 8000
DOCUMENTATION_FILE = "deploy/API_DOCUMENTATION.md"

CSS = """
<style>
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', sans-serif;
    line-height: 1.6;
    color: #333;
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
}
h1, h2, h3, h4, h5, h6 {
    margin-top: 24px;
    margin-bottom: 16px;
    font-weight: 600;
    line-height: 1.25;
}
h1 { font-size: 2em; border-bottom: 1px solid #eaecef; padding-bottom: .3em; }
h2 { font-size: 1.5em; border-bottom: 1px solid #eaecef; padding-bottom: .3em; }
code {
    background-color: rgba(27,31,35,.05);
    border-radius: 3px;
    font-size: 85%;
    margin: 0;
    padding: .2em .4em;
}
pre {
    background-color: #f6f8fa;
    border-radius: 3px;
    font-size: 85%;
    line-height: 1.45;
    overflow: auto;
    padding: 16px;
}
pre code {
    background-color: transparent;
    border: 0;
    display: inline;
    line-height: inherit;
    margin: 0;
    overflow: visible;
    padding: 0;
    word-wrap: normal;
}
</style>
"""

class DocumentationHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/API_DOCUMENTATION.md':
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open(DOCUMENTATION_FILE, 'r') as f:
                content = f.read()
                html = markdown2.markdown(content, extras=["fenced-code-blocks", "tables"])
                full_html = f"<html><head>{CSS}</head><body>{html}</body></html>"
                self.wfile.write(full_html.encode())
        else:
            self.send_error(404, "File not found")

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), DocumentationHandler) as httpd:
        print(f"Serving API documentation at http://localhost:{PORT}")
        httpd.serve_forever()