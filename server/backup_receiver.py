#!/usr/bin/env python3
"""請求書作成ツールの控えを受け取る口（書き込み専用）。

- POST /invoice-backup に取引先データ(JSON)を受け取り、日時つきファイルで保存する。
- 読み出し口は作らない（口座番号などを含むため、外から読めないようにする）。
  復元は VPS 上で backups-data/ のファイルを使う（手順は HANDOFF.md）。
- 直前と同じ中身は保存しない。古い控えは消さない（1件数KBのため）。
2026-11-16 作成：ブラウザ保存だけだったデータが消えた事故の再発防止。
"""
import hashlib, json, os, time
from collections import defaultdict, deque
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST, PORT = "127.0.0.1", 8791
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backups-data")
ALLOWED_ORIGINS = {"https://invoice-app-two-gamma.vercel.app"}
MAX_BYTES = 2 * 1024 * 1024
RATE_PER_HOUR = 240
_hits = defaultdict(deque)


def _latest_hash():
    p = os.path.join(DATA_DIR, "latest.sha256")
    try:
        with open(p) as f:
            return f.read().strip()
    except OSError:
        return ""


class H(BaseHTTPRequestHandler):
    def _cors(self):
        origin = self.headers.get("Origin", "")
        if origin in ALLOWED_ORIGINS:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
            self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.send_header("Access-Control-Max-Age", "86400")

    def _reply(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self._cors()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        self._reply(404, {"error": "not found"})

    def do_POST(self):
        if self.path.rstrip("/") != "/invoice-backup":
            return self._reply(404, {"error": "not found"})
        if self.headers.get("Origin", "") not in ALLOWED_ORIGINS:
            return self._reply(403, {"error": "origin"})
        ip = self.headers.get("X-Forwarded-For", self.client_address[0]).split(",")[0].strip()
        now = time.time()
        q = _hits[ip]
        while q and now - q[0] > 3600:
            q.popleft()
        if len(q) >= RATE_PER_HOUR:
            return self._reply(429, {"error": "rate"})
        q.append(now)
        n = int(self.headers.get("Content-Length") or 0)
        if n <= 0 or n > MAX_BYTES:
            return self._reply(413, {"error": "size"})
        raw = self.rfile.read(n)
        try:
            data = json.loads(raw)
        except ValueError:
            return self._reply(400, {"error": "json"})
        if not isinstance(data, dict) or not isinstance(data.get("clients"), dict):
            return self._reply(400, {"error": "shape"})
        canon = json.dumps(data, ensure_ascii=False, sort_keys=True).encode()
        h = hashlib.sha256(canon).hexdigest()
        if h == _latest_hash():
            return self._reply(200, {"ok": True, "saved": False, "at": None})
        ts = datetime.now()
        day = os.path.join(DATA_DIR, ts.strftime("%Y/%m/%d"))
        os.makedirs(day, mode=0o700, exist_ok=True)
        path = os.path.join(day, ts.strftime("%H%M%S") + "-" + h[:10] + ".json")
        with open(path, "wb") as f:
            f.write(canon)
        os.chmod(path, 0o600)
        tmp = os.path.join(DATA_DIR, "latest.json.tmp")
        with open(tmp, "wb") as f:
            f.write(canon)
        os.chmod(tmp, 0o600)
        os.replace(tmp, os.path.join(DATA_DIR, "latest.json"))
        with open(os.path.join(DATA_DIR, "latest.sha256"), "w") as f:
            f.write(h)
        return self._reply(200, {"ok": True, "saved": True, "at": ts.isoformat(timespec="seconds")})

    def log_message(self, fmt, *args):
        pass


if __name__ == "__main__":
    os.makedirs(DATA_DIR, mode=0o700, exist_ok=True)
    os.chmod(DATA_DIR, 0o700)
    ThreadingHTTPServer((HOST, PORT), H).serve_forever()
