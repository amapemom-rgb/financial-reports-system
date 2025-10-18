#!/usr/bin/env python3
"""
Simple HTTP server with CORS for the Financial Reports Web UI
"""

import http.server
import socketserver
from pathlib import Path

PORT = 8000

class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler with CORS headers"""
    
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

def main():
    # Change to web-ui directory
    web_ui_dir = Path(__file__).parent
    import os
    os.chdir(web_ui_dir)
    
    with socketserver.TCPServer(("", PORT), CORSHTTPRequestHandler) as httpd:
        print(f"""
╔════════════════════════════════════════════════════════╗
║  Financial Reports Analysis System - Web UI           ║
╚════════════════════════════════════════════════════════╝

🚀 Сервер запущен!

📍 Открой в браузере:
   http://localhost:{PORT}

💡 Для получения токена выполни в другом терминале:
   gcloud auth print-identity-token

🛑 Для остановки: Ctrl+C

════════════════════════════════════════════════════════
        """)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n✅ Сервер остановлен")

if __name__ == "__main__":
    main()
