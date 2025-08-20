#!/usr/bin/env python3
# Compare frontend_contract.json to endpoints detected via AST in app/api/v1

from __future__ import annotations
import json
import sys
from pathlib import Path
from typing import Dict, Tuple

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "frontend_contract.json"


def load_contract() -> Dict:
    with CONTRACT.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_detected() -> Dict:
    # Reuse AST helper
    import subprocess
    script = ROOT / "scripts" / "ast_extract.py"
    out = subprocess.check_output([sys.executable, str(script)], cwd=str(ROOT))
    return json.loads(out.decode("utf-8"))


def normalize_path(p: str) -> str:
    # AST returns router-local path (like "/users/") — our contract stores same.
    return p.rstrip("/") if p != "/" else "/"


def main(argv=None) -> int:
    contract = load_contract()
    detected = load_detected()

    # Build maps path+method -> record
    expected = {}
    for ep in contract.get("endpoints", []):
        expected[(ep["method"].upper(), normalize_path(ep["path"]))] = ep

    found = {}
    for ep in detected.get("endpoints", []):
        found[(ep["method"].upper(), normalize_path(ep["path"]))] = ep

    missing = []
    extra = []

    for k, v in expected.items():
        if k not in found:
            missing.append({"method": k[0], "path": k[1]})
    for k, v in found.items():
        if k not in expected:
            extra.append({"method": k[0], "path": k[1]})

    # RBAC role comparison (best-effort using AST dependencies)
    role_diffs = []
    for k in expected.keys():
        if k in found:
            exp_roles = set((expected[k].get("auth", {}) or {}).get("roles", []))
            det_roles = set(found[k].get("roles", []))
            if exp_roles and exp_roles != det_roles:
                role_diffs.append({
                    "method": k[0], "path": k[1],
                    "expected_roles": sorted(exp_roles),
                    "detected_roles": sorted(det_roles)
                })

    ok = not missing and not role_diffs

    report = {
        "missing_endpoints": missing,
        "extra_endpoints": extra,
        "role_differences": role_diffs,
        "detected_base_paths": detected.get("base_paths", [])
    }

    print(json.dumps(report, ensure_ascii=False, indent=2))

    if not ok:
        print("Contract validation FAILED", file=sys.stderr)
        return 1
    print("Contract validation OK")
    #!/usr/bin/env python3
    """
    Validate that the frontend_contract.json matches the actual FastAPI endpoints (via AST extractor).
    Normalizes path parameter names (e.g., {id} vs {user_id}) to avoid false mismatches.
    Treats unknown detected roles as warnings and does not fail on them.
    """
    import json
    import re
    import sys
    from pathlib import Path

    from ast_extract import extract_all


    def load_contract(path: Path):
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)


    _PARAM_RE = re.compile(r"\{[^}]+\}")


    def canonicalize_path(path: str) -> str:
        # Replace any {param_name} with {param}
        return _PARAM_RE.sub("{param}", path)


    def main():
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--contract", default="frontend_contract.json")
        parser.add_argument("--output", help="Write JSON result to this file as well")
        args = parser.parse_args()

        contract = load_contract(Path(args.contract))
        detected = extract_all(str(Path(__file__).resolve().parents[1] / "app"))

        contract_eps_raw = [(e["method"].upper(), e["path"]) for e in contract.get("endpoints", [])]
        detected_eps_raw = [(e["method"].upper(), e["path"]) for e in detected.get("endpoints", [])]

        contract_eps = {(m, canonicalize_path(p)) for (m, p) in contract_eps_raw}
        detected_eps = {(m, canonicalize_path(p)) for (m, p) in detected_eps_raw}

        missing = sorted(list(contract_eps - detected_eps))
        extra = sorted(list(detected_eps - contract_eps))

        # Role differences where both sides define roles
        role_diffs = []
        role_unknown = []

        detected_by_key = { (e["method"].upper(), canonicalize_path(e["path"])): e for e in detected.get("endpoints", []) }
        for e in contract.get("endpoints", []):
            key = (e["method"].upper(), canonicalize_path(e["path"]))
            det = detected_by_key.get(key)
            if not det:
                continue
            exp_roles = sorted(e.get("roles", []))
            det_roles = sorted(det.get("roles", []))
            if exp_roles and det_roles:
                if exp_roles != det_roles:
                    role_diffs.append({"method": key[0], "path": key[1], "expected_roles": exp_roles, "detected_roles": det_roles})
            elif exp_roles and not det_roles:
                role_unknown.append({"method": key[0], "path": key[1], "expected_roles": exp_roles, "detected_roles": []})

        result = {
            "missing_endpoints": [{"method": m, "path": p} for (m, p) in missing],
            "extra_endpoints": [{"method": m, "path": p} for (m, p) in extra],
            "role_differences": role_diffs,
            "role_unknown": role_unknown,
            "detected_base_paths": detected.get("base_paths", [])
        }

        output_json = json.dumps(result, indent=2, ensure_ascii=False)
        print(output_json)
        if args.output:
            Path(args.output).write_text(output_json, encoding="utf-8")

        # Fail only on real endpoint mismatches or concrete role diffs
        if missing or extra or role_diffs:
            print("Contract validation FAILED", file=sys.stderr)
            sys.exit(1)
        else:
            print("Contract validation OK")


    if __name__ == "__main__":
        main()
