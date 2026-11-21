"""带 COOP/COEP 头的本地服务器。

开这两个头之后浏览器才允许 SharedArrayBuffer，onnxruntime-web 才能多线程，
WASM 推理快 3~4 倍。GitHub Pages 不支持自定义头，那里由 coi-serviceworker 补。

用法: python site/serve.py [端口]
"""
import http.server
import socketserver
import sys
from pathlib import Path

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
ROOT = Path(__file__).resolve().parent


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(ROOT), **kw)

    def end_headers(self):
        self.send_header("Cross-Origin-Opener-Policy", "same-origin")
        self.send_header("Cross-Origin-Embedder-Policy", "require-corp")
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer(("", PORT), Handler) as httpd:
        print(f"http://127.0.0.1:{PORT}/  (多线程已启用)")
        httpd.serve_forever()
