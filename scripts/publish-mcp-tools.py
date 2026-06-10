from __future__ import annotations

"""Publish Upwind production-table KQL files as Microsoft Sentinel custom MCP tools."""

import argparse
import json
import pathlib
import re
import subprocess
import sys
import urllib.error
import urllib.request

SENTINEL_RESOURCE_ID = "4500ebfb-89b6-4b14-a480-7f749797bfcd"
API_BASE = "https://api.securityplatform.microsoft.com/aiprimitives/mcpToolCollections"

DESCRIPTIONS = {
    "Defender_Exposure_Asset_Context": "Retrieve Microsoft Security Exposure Management graph node context for a supplied asset name, VM name, cloud resource ID, or other known entity identifier.",
    "Defender_Exposure_Asset_Relationships": "Retrieve direct inbound and outbound Microsoft Security Exposure Management graph relationships for a supplied asset so an agent can reason over attack-path context.",
    "Upwind_Cloud_Risk_Posture_Summary": "Summarize production Upwind cloud asset posture: assets, critical/high risk, internet exposure, sensitive data, unprotected assets, risk scores, providers, accounts, and regions.",
    "Upwind_Internet_Facing_Critical_Risk": "Find internet-facing Upwind assets with critical or high network, vulnerability, or detection risk and show public IPs, technologies, and combined risk score.",
    "Upwind_Sensitive_Data_Exposure": "Surface Upwind assets with sensitive data at rest or in transit, joined to network, detection, vulnerability, privilege, internet exposure, and protection context.",
    "Upwind_High_Privilege_Risk_Hunt": "Hunt Upwind assets with high privilege risk and calculate blast-radius context from public exposure, network risk, and vulnerability risk.",
    "Upwind_Vulnerability_Hotspots": "Rank Upwind vulnerability hotspots by cloud account and region, including KEV exposure, internet-facing KEV assets, CVE counts, technologies, and resource types.",
    "Upwind_Detection_Risk_Triage": "Triage Upwind runtime detection risk by asset with severity level, score, MITRE tactic/technique, public exposure, sensitive data, and triage tier.",
    "Upwind_Asset_Risk_Investigation": "Investigate a supplied Upwind asset name, resource ID, or asset ID across network, detection, vulnerability, privilege, sensitive-data, IP, technology, and aggregate risk context.",
}

ARGUMENT_DESCRIPTIONS = {
    "AssetName": "Asset name, cloud resource ID, VM name, workload name, or other identifying substring to investigate.",
}

PLACEHOLDER_PATTERN = re.compile(r"(?<!{){\s*([A-Za-z_][A-Za-z0-9_]*)\s*}(?!})")


def az_token() -> str:
    completed = subprocess.run(
        ["az", "account", "get-access-token", "--resource", SENTINEL_RESOURCE_ID, "--query", "accessToken", "-o", "tsv"],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def request(method: str, url: str, token: str, payload: dict, *, allow_conflict: bool = False) -> dict:
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        method=method,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        if allow_conflict and exc.code == 409:
            return {"status": "exists", "details": details}
        raise RuntimeError(f"{method} {url} failed: HTTP {exc.code}: {details}") from exc


def tool_payload(collection: str, workspace_id: str, query_path: pathlib.Path) -> dict:
    name = query_path.stem
    query_format = query_path.read_text().strip()
    placeholders = sorted({match.group(1) for match in PLACEHOLDER_PATTERN.finditer(query_format)})
    argument_properties = {
        "workspaceId": {"type": "string", "description": "Log Analytics workspace/customer ID to query."}
    }
    required_arguments = ["workspaceId"]
    for placeholder in placeholders:
        if placeholder == "workspaceId":
            continue
        argument_properties[placeholder] = {
            "type": "string",
            "description": ARGUMENT_DESCRIPTIONS.get(placeholder, f"Value to substitute for {placeholder}."),
        }
        required_arguments.append(placeholder)

    return {
        "name": name,
        "title": name.replace("_", " "),
        "description": DESCRIPTIONS.get(name, f"Run the {name.replace('_', ' ')} KQL investigation."),
        "collectionName": collection,
        "properties": {
            "mcpToolType": "Kqs",
            "queryFormat": query_format,
            "arguments": {
                "type": "object",
                "properties": argument_properties,
                "required": required_arguments,
            },
            "defaultArgumentValues": {"workspaceId": workspace_id},
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Publish production Upwind KQL files as Sentinel custom MCP tools.")
    parser.add_argument("--collection", default="Upwind-Sentinel-MCP-Tools")
    parser.add_argument("--workspace-id", required=True)
    parser.add_argument("--tools-dir", default=str(pathlib.Path(__file__).parents[1] / "mcp-tools"))
    parser.add_argument("--dry-run", action="store_true", help="Print collection/tool payloads without calling the Sentinel authoring API.")
    args = parser.parse_args()

    collection_payload = {
        "name": args.collection,
        "title": "Upwind and Defender Exposure Sentinel Custom MCP Tools",
        "description": "Custom Sentinel MCP tools for production Upwind cloud asset risk plus separate Defender Exposure Management graph context. Agents can call both tool families to combine exposure and runtime-risk evidence.",
    }
    print(f"Publishing collection: {args.collection}")
    if args.dry_run:
        print(json.dumps(collection_payload, indent=2))
        token = ""
    else:
        token = az_token()
        print(json.dumps(request("PUT", f"{API_BASE}/{args.collection}", token, collection_payload, allow_conflict=True), indent=2))

    for query_path in sorted(pathlib.Path(args.tools_dir).glob("*.kql")):
        payload = tool_payload(args.collection, args.workspace_id, query_path)
        print(f"\nPublishing tool: {payload['name']}")
        if args.dry_run:
            print(json.dumps(payload, indent=2))
        else:
            print(json.dumps(request("PUT", f"{API_BASE}/{args.collection}/tools/{payload['name']}", token, payload), indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())
