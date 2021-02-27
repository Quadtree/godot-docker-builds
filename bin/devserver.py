import http.server
import os

print('Dev server starting up on port 8080')

class ReqHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        if '.css.gz' in self.path or '.js.gz' in self.path:
            self.send_header('Content-Encoding', 'gzip')

        self.send_header('Cross-Origin-Opener-Policy', 'same-origin')
        self.send_header('Cross-Origin-Embedder-Policy', 'require-corp')

        super(ReqHandler, self).end_headers()

server = http.server.HTTPServer(('0.0.0.0', 8080), ReqHandler)
server.serve_forever()