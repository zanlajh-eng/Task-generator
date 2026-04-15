import http.server, os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

class H(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "":
            self.path = "/campaign-task-generator.html"
        return super().do_GET()
    def log_message(self, *a): pass

http.server.HTTPServer(("", 3456), H).serve_forever()
