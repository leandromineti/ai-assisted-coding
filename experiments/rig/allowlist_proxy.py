#!/usr/bin/env python3
"""Minimal CONNECT proxy with a host allowlist.

Runs from the pinned rig image (stdlib only) so the "package-hosts-only" network
condition needs no additional image. Arms sit on a --internal Docker network with
no route off-host; this proxy is the only path out, and it refuses any host not
on the allowlist. Denials are logged so the log can carry a probe record.
"""
import socket
import sys
import threading

PORT = 8888
ALLOWED = {
    "pypi.org",
    "files.pythonhosted.org",
    "pypi.python.org",
    # 2026-08-17: model API, added for the first agent runs under this condition
    # (exp-02 escalation screening). The 2026-07-31 probes were curl/pip only, so
    # the in-container harness had never needed egress before. Anything else the
    # harness tries (telemetry etc.) stays denied and shows up in the proxy log —
    # that is the probe record, not a problem to silence.
    "api.anthropic.com",
}


def allowed(host: str) -> bool:
    host = host.lower().split(":")[0]
    return any(host == a or host.endswith("." + a) for a in ALLOWED)


def relay(a: socket.socket, b: socket.socket) -> None:
    try:
        while True:
            data = a.recv(65536)
            if not data:
                break
            b.sendall(data)
    except OSError:
        pass
    finally:
        for s in (a, b):
            try:
                s.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass


def handle(client: socket.socket) -> None:
    try:
        client.settimeout(20)
        req = b""
        while b"\r\n\r\n" not in req:
            chunk = client.recv(4096)
            if not chunk:
                return
            req += chunk
            if len(req) > 65536:
                return
        line = req.split(b"\r\n", 1)[0].decode("latin-1")
        parts = line.split()
        if len(parts) < 2:
            return
        method, target = parts[0], parts[1]

        if method.upper() == "CONNECT":
            host, _, port = target.partition(":")
            port = int(port or 443)
        else:
            # Plain HTTP: derive host from the Host header.
            host, port = "", 80
            for h in req.decode("latin-1").split("\r\n")[1:]:
                if h.lower().startswith("host:"):
                    host = h.split(":", 1)[1].strip()
                    break
            if ":" in host:
                host, _, p = host.partition(":")
                port = int(p)

        if not host or not allowed(host):
            print(f"DENY {method} {host}:{port}", flush=True)
            client.sendall(b"HTTP/1.1 403 Forbidden\r\nContent-Length: 34\r\n\r\n"
                           b"blocked by rig allowlist proxy\n")
            return

        print(f"ALLOW {method} {host}:{port}", flush=True)
        upstream = socket.create_connection((host, port), timeout=20)
        if method.upper() == "CONNECT":
            client.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")
        else:
            upstream.sendall(req)
        client.settimeout(None)
        upstream.settimeout(None)
        t = threading.Thread(target=relay, args=(client, upstream), daemon=True)
        t.start()
        relay(upstream, client)
    except Exception as exc:  # noqa: BLE001 - proxy must never die on one client
        print(f"ERROR {exc!r}", flush=True)
    finally:
        try:
            client.close()
        except OSError:
            pass


def main() -> None:
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("0.0.0.0", PORT))
    srv.listen(64)
    print(f"allowlist proxy on :{PORT}; allowed={sorted(ALLOWED)}", flush=True)
    while True:
        client, _ = srv.accept()
        threading.Thread(target=handle, args=(client,), daemon=True).start()


if __name__ == "__main__":
    sys.exit(main())
