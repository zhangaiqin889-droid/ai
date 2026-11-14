"""Deterministic parity report: never convert a scoped test score into whole-product coverage."""
import json
from pathlib import Path

def summarize(matrix, test_results):
    features = matrix.get("features", [])
    if not isinstance(features, list):
        raise ValueError("Invalid feature matrix")
    results = test_results.get("results", [])
    if not isinstance(results, list):
        raise ValueError("Invalid results")
    indexed = {}
    for item in results:
        if item["id"] in indexed:
            raise ValueError("Duplicate test result")
        indexed[item["id"]] = item
    known = {f["id"] for f in features}
    if len(known) != len(features):
        raise ValueError("Duplicate features")
    if any(i not in known for i in indexed):
        raise ValueError("Result for unknown feature")
    rows = []
    for feature in features:
        r = indexed.get(feature["id"])
        rows.append({"id": feature["id"], "name": feature["name"], "status": (
            "PASS" if r and r.get("pass") is True else
            "FAIL" if r and r.get("pass") is False else "NOT_VERIFIED")})
    passed = sum(row["status"]=="PASS" for row in rows)
    failed = sum(row["status"]=="FAIL" for row in rows)
    return {
        "scope": "discovered OpenAPI features only",
        "known_features": len(rows), "passed": passed, "failed": failed,
        "not_verified": len(rows)-passed-failed,
        "measured_pass_fraction": passed/len(rows) if rows else None,
        "whole_software_recreation_rate": "UNKNOWN",
        "features": rows,
    }

def main():
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("matrix_json")
    p.add_argument("result_json")
    a=p.parse_args()
    matrix=json.loads(Path(a.matrix_json).read_text(encoding="utf-8"))
    results=json.loads(Path(a.result_json).read_text(encoding="utf-8"))
    print(json.dumps(summarize(matrix,results),ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
