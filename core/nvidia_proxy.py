"""
NVIDIA NIM Proxy for claw-code
"""
import http.server
import json
import urllib.request
import os
import sys
import traceback

NVIDIA_URL = "https://integrate.api.nvidia.com"
NVIDIA_KEY = os.environ.get("NVIDIA_API_KEY", "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")

MODEL_MAP = {
    "deepseek-v4-flash": "openai/gpt-oss-20b",
    "deepseek-v4-pro": "openai/gpt-oss-20b",
    "kimi-k2.5": "qwen/qwen3.5-397b-a17b",
    "minimax-m2.7": "mistralai/mistral-large-3-675b-instruct-2512",
    "cosmos-nemotron": "nvidia/llama-3.3-nemotron-super-49b-v1.5",
    "llama-4-maverick": "meta/llama-3.3-70b-instruct",
    "llama-3.3-70b": "meta/llama-3.3-70b-instruct",
    "qwen3-coder": "qwen/qwen3.5-397b-a17b",
    "qwen3.5-397b": "qwen/qwen3.5-397b-a17b",
    "nemotron-super-49b": "nvidia/llama-3.3-nemotron-super-49b-v1.5",
    "mistral-large-3": "mistralai/mistral-large-3-675b-instruct-2512",
    "gpt-oss-20b": "openai/gpt-oss-20b",
}

def resolve_model(short):
    return MODEL_MAP.get(short, short)

class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length) if length else b"{}"
            body = json.loads(raw)

            if "model" in body:
                original = body["model"]
                body["model"] = resolve_model(original)
                sys.stderr.write(f"MODEL: {original} -> {body['model']}\n")
                sys.stderr.flush()

            url = NVIDIA_URL + self.path
            sys.stderr.write(f"URL: {url}\n")
            sys.stderr.flush()

            data = json.dumps(body).encode()
            req = urllib.request.Request(url, data=data, method="POST")
            req.add_header("Content-Type", "application/json")
            req.add_header("Authorization", f"Bearer {NVIDIA_KEY}")

            with urllib.request.urlopen(req, timeout=300) as resp:
                content = resp.read()
                self.send_response(resp.status)
                ct = resp.getheader("Content-Type", "application/json")
                self.send_header("Content-Type", ct)
                self.end_headers()
                self.wfile.write(content)
                sys.stderr.write(f"OK: {len(content)} bytes\n")
                sys.stderr.flush()

        except urllib.error.HTTPError as e:
            error_body = e.read()
            sys.stderr.write(f"HTTP ERROR {e.code}: {error_body[:200]}\n")
            sys.stderr.flush()
            self.send_response(e.code)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(error_body)
        except Exception as e:
            tb = traceback.format_exc()
            sys.stderr.write(f"EXCEPTION: {tb}\n")
            sys.stderr.flush()
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def do_GET(self):
        if self.path == "/v1/models" or self.path == "/models":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            models = [{"id": k, "object": "model"} for k in MODEL_MAP.values()]
            self.wfile.write(json.dumps({"object": "list", "data": models}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, fmt, *args):
        sys.stderr.write(f"LOG: {fmt % args}\n")
        sys.stderr.flush()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8082
    server = http.server.HTTPServer(("127.0.0.1", port), ProxyHandler)
    sys.stderr.write(f"NVIDIA proxy on http://127.0.0.1:{port}\n")
    sys.stderr.flush()
    server.serve_forever()
