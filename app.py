import os
import sys
import subprocess
import shutil
import threading
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.request import urlopen, Request
from urllib.error import HTTPError

PROXY_PORT = 9191

class NotionProxyHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length)
        try:
            payload = json.loads(raw)
            api_key = payload["apiKey"]
            notion_body = json.dumps(payload["body"]).encode()
            req = Request(
                "https://api.notion.com/v1/pages",
                data=notion_body,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "Notion-Version": "2022-06-28",
                },
                method="POST"
            )
            try:
                with urlopen(req) as resp:
                    data = resp.read()
                    status = resp.status
            except HTTPError as e:
                data = e.read()
                status = e.code
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            self.send_response(500)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(str(e).encode())

    def log_message(self, *args):
        pass

# 1. Zaženemo lokalni proxy — bind se zgodi takoj, serve_forever v ozadju
# Če je port zaseden (prejšnja instanca), to ignoriramo — proxy že teče
class ReusableHTTPServer(HTTPServer):
    allow_reuse_address = True

try:
    _proxy_server = ReusableHTTPServer(("127.0.0.1", PROXY_PORT), NotionProxyHandler)
    threading.Thread(target=_proxy_server.serve_forever, daemon=True).start()
except OSError:
    pass  # Proxy že teče na tem portu iz prejšnje instance

def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# 2. Poiščemo vgrajen HTML
source_html = get_resource_path("campaign-task-generator.html")

# 3. Prepišemo ga v lokalno mapo, kjer je EXE
if hasattr(sys, '_MEIPASS'):
    exe_dir = os.path.dirname(sys.executable)
else:
    exe_dir = os.path.dirname(os.path.abspath(__file__))
target_html = os.path.join(exe_dir, "view_generator.html")
try:
    shutil.copy(source_html, target_html)
except:
    pass

# 4. Zaženemo Edge
edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if not os.path.exists(edge_path):
    edge_path = "msedge"

cmd = [
    edge_path,
    f"--app=file:///{target_html}",
    "--disable-web-security",
    "--user-data-dir=C:/temp_edge_generator",
    "--no-first-run",
    "--disable-sync",
    "--disable-extensions",
    "--no-default-browser-check",
    "--disable-background-networking",
]

proc = subprocess.Popen(cmd)
proc.wait()  # Čakamo da Edge zapre okno, nato se proxy ustavi
