from __future__ import annotations

"""Interactive terminal runner for the Upwind Sentinel custom MCP tools."""

import argparse
import asyncio
import json
import os
import re
from typing import Any

from dotenv import load_dotenv

from sentinel_mcp_tools.client import MCPToolResult, SentinelMCPClient


UPWIND_TOOLS = {
    "posture": "Upwind_Cloud_Risk_Posture_Summary",
    "internet": "Upwind_Internet_Facing_Critical_Risk",
    "sensitive": "Upwind_Sensitive_Data_Exposure",
    "privilege": "Upwind_High_Privilege_Risk_Hunt",
    "vulnerability": "Upwind_Vulnerability_Hotspots",
    "detection": "Upwind_Detection_Risk_Triage",
    "asset": "Upwind_Asset_Risk_Investigation",
}

TOOL_ROUTES = [
    (("asset", "workload", "resource", "vm ", "investigate"), UPWIND_TOOLS["asset"]),
    (("internet", "public", "exposed", "facing", "public ip"), UPWIND_TOOLS["internet"]),
    (("sensitive", "pii", "pci", "phi", "secret", "data exposure"), UPWIND_TOOLS["sensitive"]),
    (("privilege", "iam", "admin", "blast radius", "key vault"), UPWIND_TOOLS["privilege"]),
    (("vuln", "cve", "kev", "patch", "vulnerability"), UPWIND_TOOLS["vulnerability"]),
    (("detection", "runtime", "mitre", "triage", "containment"), UPWIND_TOOLS["detection"]),
]

EXAMPLE_PROMPTS = [
    "Summarize Upwind cloud risk posture",
    "Show internet-facing critical Upwind risk",
    "Show Upwind sensitive data exposure",
    "Hunt high privilege Upwind risk",
    "Show Upwind vulnerability hotspots",
    "Triage Upwind runtime detection risk",
    "Investigate Upwind asset vm-web-prod-01",
]


def parse_json_env(name: str, default: dict[str, Any]) -> dict[str, Any]:
    raw = os.getenv(name)
    if not raw:
        return default
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{name} must be valid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be a JSON object.")
    return value


def extract_asset(message: str) -> str:
    quoted = re.search(r"['\"]([^'\"]+)['\"]", message)
    if quoted:
        return quoted.group(1)
    match = re.search(r"\b(?:vm|pod|aks|eks|gke|prd|prod|dev|staging)[\w.-]*\b", message, re.IGNORECASE)
    if match:
        return match.group(0)
    fallback = os.getenv("UPWIND_ASSET_NAME")
    if fallback and not fallback.startswith("<"):
        return fallback
    raise ValueError("Asset investigation requires a quoted asset value in the prompt or UPWIND_ASSET_NAME in the environment.")


def render_arguments(message: str, tool_name: str, template: str, defaults: dict[str, Any]) -> dict[str, Any]:
    rendered = template.replace("{message}", message)
    try:
        args = json.loads(rendered)
    except json.JSONDecodeError as exc:
        raise ValueError(f"MCP_TOOL_ARGUMENT_TEMPLATE rendered invalid JSON: {exc}") from exc
    if not isinstance(args, dict):
        raise ValueError("MCP_TOOL_ARGUMENT_TEMPLATE must render to a JSON object.")
    merged = {**args, **defaults}
    if tool_name == UPWIND_TOOLS["asset"]:
        merged.setdefault("AssetName", extract_asset(message))
    return merged


def select_tool(prompt: str) -> str:
    configured = os.getenv("SENTINEL_MCP_TOOL", "").strip()
    prompt_lower = prompt.lower()
    for keywords, tool_name in TOOL_ROUTES:
        if any(keyword in prompt_lower for keyword in keywords):
            return tool_name
    return configured or UPWIND_TOOLS["posture"]


def create_mcp_client() -> SentinelMCPClient:
    return SentinelMCPClient(
        collection=os.getenv("SENTINEL_MCP_COLLECTION"),
        server_url=os.getenv("SENTINEL_MCP_SERVER_URL"),
    )


async def run_prompt(prompt: str, *, show_raw: bool) -> None:
    tool_name = select_tool(prompt)
    template = os.getenv("MCP_TOOL_ARGUMENT_TEMPLATE", "{}")
    defaults = parse_json_env("MCP_DEFAULT_ARGUMENTS", {})
    arguments = render_arguments(prompt, tool_name, template, defaults)

    print(f"\nPrompt: {prompt}")
    print(f"Tool:   {tool_name}")
    print(f"Args:   {json.dumps(arguments, sort_keys=True)}")
    print("Status: calling Sentinel MCP...\n")

    client = create_mcp_client()
    await client.connect()
    try:
        result: MCPToolResult = await client.call_tool(tool_name, arguments)
    finally:
        await client.close()

    raw_text = result.text or json.dumps(result.content, indent=2)
    print("Result")
    print("------")
    print(raw_text)


async def interactive_loop(show_raw: bool) -> None:
    print("Upwind Sentinel Custom MCP Tool Runner")
    print("Type a prompt and press Enter. Type 'examples' to list prompts or 'quit' to exit.\n")
    print("Examples:")
    for prompt in EXAMPLE_PROMPTS:
        print(f"  - {prompt}")

    while True:
        try:
            prompt = input("\nupwind-mcp> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return

        if not prompt:
            continue
        if prompt.lower() in {"quit", "exit", "q"}:
            return
        if prompt.lower() == "examples":
            for example in EXAMPLE_PROMPTS:
                print(f"  - {example}")
            continue

        try:
            await run_prompt(prompt, show_raw=show_raw)
        except Exception as exc:
            print(f"Error: {exc}")


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="Run the Upwind Sentinel custom MCP terminal client.")
    parser.add_argument("--prompt", help="Run one prompt and exit instead of starting the interactive loop.")
    parser.add_argument("--show-raw", action="store_true", help="Print the formatted raw MCP/Kusto result.")
    args = parser.parse_args()

    if args.prompt:
        asyncio.run(run_prompt(args.prompt, show_raw=args.show_raw))
    else:
        asyncio.run(interactive_loop(show_raw=args.show_raw))


if __name__ == "__main__":
    main()
