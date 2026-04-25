"""Minimal static file server for landing page."""
import http.server, os
os.chdir(os.path.join(os.path.dirname(__file__)))
http.server.HTTPServer(("0.0.0.0", 3000), http.server.SimpleHTTPRequestHandler).serve_forever()
