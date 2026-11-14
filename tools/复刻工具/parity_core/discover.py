"""Offline OpenAPI 3.x discovery: evidence-backed feature matrix, no network calls."""
import hashlib
import json
import re
from pathlib import Path

METHODS = ("get", "head", "post", "put", "patch", "delete", "options", "trace")

def discover(spec):
    if not isinstance(spec, dict) or not isinstance(spec.get("paths"), dict):
        raise ValueError("Input must be an OpenAPI document with a paths object")
    result = []
    seen = set()
    for path, item in sorted(spec["paths"].items()):
        if not isinstance(path, str) or not path.startswith("/") or not isinstance(item, dict):
            continue
        for method in METHODS:
            operation = item.get(method)
            if not isinstance(operation, dict):
                continue
            fid = "api_" + hashlib.sha256((method.upper()+" "+path).encode()).hexdigest()[:12]
            if fid in seen:
                raise ValueError("Feature id collision")
            seen.add(fid)
            result.append({
                "id": fid, "name": operation.get("summary") or operation.get("operationId") or method.upper()+" "+path,
                "kind": "api", "method": method.upper(), "path": path,
                "tags": operation.get("tags", []),
                "source": "openapi", "source_evidence": {"operation_id": operation.get("operationId"), "path": path, "method": method},
                "status": "DISCOVERED_NOT_VERIFIED",
                "testable_read_only": method in ("get", "head") and not re.search(r"\{[^{}]+\}", path),
                "auth_declared": "security" in operation or "security" in spec,
                "implementation": "UNKNOWN",
            })
    return {"source_type": "openapi", "feature_count": len(result), "features": result,
            "limitations": "OpenAPI describes declared endpoints, not undocumented UI, private backend implementation, or actual functionality."}

def read_spec(path):
    p = Path(path)
    if p.suffix.lower() != ".json":
        raise ValueError("Only local JSON OpenAPI files supported, no URL fetching")
    if p.stat().st_size > 4*1024*1024:
        raise ValueError("File is too large")
    return json.loads(p.read_text(encoding="utf-8"))

def read_only_plan(matrix):
    if not isinstance(matrix, dict) or not isinstance(matrix.get("features"), list):
        raise ValueError("Invalid feature matrix")
    cases = [{"id": f["id"], "method": f["method"], "path": f["path"]}
             for f in matrix["features"] if f.get("testable_read_only")]
    return {"cases": cases, "excluded": [f["id"] for f in matrix["features"] if not f.get("testable_read_only")],
            "limitations": "Read-only endpoint plans are not comprehensive full-software parity tests."}

def main():
    import argparse
    p=argparse.ArgumentParser(description="Offline authorized OpenAPI feature discovery")
    p.add_argument("spec_json")
    p.add_argument("--output", help="Output JSON path; omit to print")
    p.add_argument("--plan", action="store_true", help="Output read-only GET/HEAD test plan")
    a=p.parse_args()
    matrix=discover(read_spec(a.spec_json))
    output=read_only_plan(matrix) if a.plan else matrix
    payload=json.dumps(output,ensure_ascii=False,indent=2)
    if a.output:
        Path(a.output).write_text(payload+"\n",encoding="utf-8")
    else:
        print(payload)

if __name__ == "__main__":
    main()
