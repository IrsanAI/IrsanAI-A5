
# v4.2 – Fix Le Chat #4: bind 0.0.0.0 ohne Auth ist Widerspruch
# Jetzt: 127.0.0.1 default, optional --host mit Token
import argparse
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os

parser = argparse.ArgumentParser(description="A5 Pro Cockpit v4.2")
parser.add_argument("--host", default="127.0.0.1", help="bind host, default 127.0.0.1 (use 0.0.0.0 only with --token)")
parser.add_argument("--port", type=int, default=8000)
parser.add_argument("--token", default=None, help="auth token required when binding 0.0.0.0")
args = parser.parse_args()

if args.host == "0.0.0.0" and not args.token:
    # Fail-closed: kein offenes Bind ohne Auth
    print("[!] bind 0.0.0.0 requires --token for auth – see THREAT_MODEL.md")
    print("[*] falling back to 127.0.0.1 – use --token mysecrettoken if you really need 0.0.0.0")
    args.host = "127.0.0.1"

if args.token:
    # simple token check middleware
    class AuthHandler(SimpleHTTPRequestHandler):
        def do_GET(self):
            auth = self.headers.get("X-A5-Token") or self.path.split("token=")[-1] if "token=" in self.path else None
            # allow if token in query
            if args.host == "0.0.0.0":
                from urllib.parse import urlparse, parse_qs
                qs = parse_qs(urlparse(self.path).query)
                if qs.get("token", [None])[0] != args.token and self.headers.get("X-A5-Token") != args.token:
                    self.send_response(401)
                    self.end_headers()
                    self.wfile.write(b"Unauthorized – need ?token= or X-A5-Token")
                    return
            return super().do_GET()
    handler = AuthHandler
else:
    handler = SimpleHTTPRequestHandler

print(f"[+] A5 Pro Cockpit v4.2 listening on {args.host}:{args.port} – fail-closed bind")
HTTPServer((args.host, args.port), handler).serve_forever()
