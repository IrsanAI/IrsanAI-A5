# v4.3 – Le Chat Fix #4: dead code removed, constant-time, no token in query, no CWD leak
import argparse, os, pathlib, hmac
from http.server import HTTPServer, SimpleHTTPRequestHandler

parser = argparse.ArgumentParser(description="A5 Pro Cockpit v4.3")
parser.add_argument("--host", default="127.0.0.1", help="bind host, default 127.0.0.1")
parser.add_argument("--port", type=int, default=8000)
parser.add_argument("--token", default=None, help="auth token required when binding 0.0.0.0")
parser.add_argument("--root", default=None, help="serve root, default ./cockpit/dist – prevents serving a5_evidence")
args = parser.parse_args()

if args.host == "0.0.0.0" and not args.token:
    print("[!] bind 0.0.0.0 requires --token – see THREAT_MODEL.md")
    print("[*] falling back to 127.0.0.1")
    args.host = "127.0.0.1"

serve_root = pathlib.Path(args.root) if args.root else pathlib.Path(__file__).parent / "dist"
if not serve_root.exists():
    serve_root = pathlib.Path.cwd() / "extensions" / "cockpit" / "dist"
    if not serve_root.exists():
        print(f"[!] dist not found at {serve_root} – fail-closed, exit")
        import sys; sys.exit(1)

os.chdir(serve_root)
print(f"[+] Serving {serve_root} on {args.host}:{args.port}")

if args.token:
    class AuthHandler(SimpleHTTPRequestHandler):
        def do_GET(self):
            header_token = self.headers.get("X-A5-Token") or self.headers.get("Authorization","").replace("Bearer ","")
            if not header_token or not hmac.compare_digest(header_token, args.token):
                self.send_response(401)
                self.end_headers()
                self.wfile.write(b"Unauthorized – need X-A5-Token header")
                return
            return super().do_GET()
    handler = AuthHandler
else:
    handler = SimpleHTTPRequestHandler

HTTPServer((args.host, args.port), handler).serve_forever()
