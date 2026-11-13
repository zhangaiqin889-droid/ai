"""Deterministic, read-only HTTP JSON parity checker for authorized hosts."""
import json
import urllib.request
import urllib.error
from urllib.parse import urlparse

def verify_target(base_url, allowed_hosts):
    p = urlparse(base_url)
    if p.scheme != "https" or p.hostname not in allowed_hosts or p.username or p.password or p.query or p.fragment:
        raise ValueError("Target must be an approved HTTPS host")
    return base_url.rstrip("/")

def fetch(base_url, case, allowed_hosts, timeout=8):
    base = verify_target(base_url, allowed_hosts)
    method = case.get("method", "GET").upper()
    if method not in ("GET", "HEAD"):
        raise ValueError("Only read-only GET/HEAD requests are permitted")
    path = case["path"]
    if not isinstance(path, str) or not path.startswith("/") or path.startswith("//") or "://" in path or "?" in path or "#" in path or "\\" in path:
        raise ValueError("Unsafe path")
    req = urllib.request.Request(base + path, method=method, headers={"Accept": "application/json"})
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            raise ValueError("Redirects blocked")
    try:
        with urllib.request.build_opener(NoRedirect()).open(req, timeout=timeout) as resp:
            body = resp.read(1024 * 1024 + 1)
            if len(body) > 1024 * 1024:
                raise ValueError("Response too large")
            return {"status": resp.status, "json": json.loads(body) if method == "GET" and body else None}
    except urllib.error.HTTPError as exc:
        if exc.code in (301, 302, 303, 307, 308):
            raise ValueError("Redirects blocked")
        return {"status": exc.code, "json": None}

def compare(original, rebuilt, case_id):
    return {"id": case_id, "pass": original == rebuilt, "original": original, "rebuilt": rebuilt}

def run_plan(plan, original_base, rebuilt_base, allowed_hosts):
    if not isinstance(plan.get("cases"), list) or not plan["cases"] or len(plan["cases"]) > 100:
        raise ValueError("Cases must contain 1-100 tests")
    seen, results = set(), []
    for case in plan["cases"]:
        cid = case["id"]
        if cid in seen:
            raise ValueError("Duplicate test ID")
        seen.add(cid)
        a = fetch(original_base, case, allowed_hosts)
        b = fetch(rebuilt_base, case, allowed_hosts)
        results.append(compare(a, b, cid))
    return {"passed": sum(r["pass"] for r in results), "total": len(results), "results": results}
