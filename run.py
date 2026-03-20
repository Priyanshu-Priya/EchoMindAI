"""
Resonance Bot — Telegram content curation assistant.
Run this file to start the bot.
"""

# from bot.main import main

# if __name__ == "__main__":
#     main()

# Alternate fix for Render WebService
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import os
from bot.main import main

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

def run_web():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), Handler)
    server.serve_forever()

if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    main()