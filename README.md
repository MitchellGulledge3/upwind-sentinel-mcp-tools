# Upwind Sentinel Custom MCP Tools

Alpha-ready custom MCP tool collection for Upwind cloud asset risk data in Microsoft Sentinel.

This repository is for an Upwind ISV developer, partner engineer, or joint customer team that wants an agent surface such as GitHub Copilot in VS Code, Copilot Studio, Foundry, Security Copilot, or a product-owned agent to call focused Upwind investigation tools over Sentinel data.

The repo does **not** ingest or generate telemetry. It assumes the customer already has an Upwind Sentinel connector sending production Upwind cloud-asset data into Sentinel. It also includes separate Defender Exposure Management graph tools so an agent can call Defender and Upwind tools independently and combine the results.

| Upwind source | Sentinel table queried by these tools | Required signal |
| --- | --- | --- |
| Upwind Catalog Loader / Upwind asset connector | `UpwindCatalogAssets_CL` | PascalCase fields such as `AssetName`, `CloudProvider`, `CloudAccountId`, `Region`, `ResourceType`, `PublicIpAddresses`, `NetworkRisk`, `DetectionRisk`, `VulnerabilityRisk`, `HighPrivilegeRisk`, `SensitiveDataAtRest`, `SensitiveDataInTransit` |
| Earlier Upwind asset table naming | `UpwindLogsAssets_CL` | Same logical fields, often lower snake_case such as `name`, `cloud_provider`, `network_risk`, `public_ip_addresses` |

The Upwind tools query only Upwind tables. The Defender tools query only Microsoft Security Exposure Management advanced hunting tables. No individual tool joins Upwind and Defender data; the consuming agent performs the correlation by invoking both tool families.

If both `UpwindCatalogAssets_CL` and `UpwindLogsAssets_CL` are populated during a connector migration, aggregate tools may count the same asset from both tables. Prefer one production connector/table per workspace for clean counts.

## What this publishes

`scripts/publish-mcp-tools.py` calls the Sentinel Platform Services authoring API and publishes each file in `mcp-tools/*.kql` as a Kqs custom MCP tool under one collection, defaulting to:

```text
Upwind-Sentinel-MCP-Tools
```

Runtime endpoint:

```text
https://sentinel.microsoft.com/mcp/custom/Upwind-Sentinel-MCP-Tools/
```

## Tools

| Tool | Main table(s) | What it answers |
| --- | --- | --- |
| `Defender_Exposure_Asset_Context` | `ExposureGraphNodes` | What does Microsoft Security Exposure Management know about this asset/entity? |
| `Defender_Exposure_Asset_Relationships` | `ExposureGraphNodes`, `ExposureGraphEdges` | What direct inbound/outbound graph relationships and attack-path context surround this asset/entity? |
| `Upwind_Cloud_Risk_Posture_Summary` | `UpwindCatalogAssets_CL`, `UpwindLogsAssets_CL` | What is the 24h Upwind posture: assets, critical/high risk, internet exposure, sensitive data, unprotected assets, risk scores, providers, accounts, and regions? |
| `Upwind_Internet_Facing_Critical_Risk` | same | Which internet-facing Upwind assets have critical/high network, vulnerability, or runtime detection risk? |
| `Upwind_Sensitive_Data_Exposure` | same | Which assets contain sensitive data and also have internet exposure, no protection, vulnerabilities, detections, or privilege risk? |
| `Upwind_High_Privilege_Risk_Hunt` | same | Which assets have high privilege risk and the largest blast-radius context? |
| `Upwind_Vulnerability_Hotspots` | same | Which accounts/regions have the worst vulnerability concentrations, KEV exposure, and internet-facing CVE risk? |
| `Upwind_Detection_Risk_Triage` | same | Which runtime detections should be contained or investigated first, based on severity, MITRE context, exposure, and sensitive-data context? |
| `Upwind_Asset_Risk_Investigation` | same | For a supplied `AssetName`, what is the full Upwind risk profile for that asset? |

For detailed usage, input arguments, KQL strategy, and expected output shape, see [`docs/tool-reference.md`](docs/tool-reference.md).

## Prerequisites

1. A Microsoft Sentinel workspace with Sentinel Platform Services / data lake enabled.
2. Production Upwind data already flowing into `UpwindCatalogAssets_CL` or `UpwindLogsAssets_CL`.
3. Microsoft Defender XDR / Microsoft Security Exposure Management advanced hunting access if you want to use `Defender_Exposure_*` tools.
4. Azure CLI authenticated to the tenant that owns the Sentinel workspace:
   ```bash
   az login
   az account set --subscription "<subscription-id-or-name>"
   ```
5. Permission to author custom MCP collections in Sentinel Platform Services.
6. Python 3.9+.

This is an alpha/private-preview style surface. The publisher and runtime both use the Sentinel Platform Services resource ID `4500ebfb-89b6-4b14-a480-7f749797bfcd`. In practice:

- The tenant must have Microsoft Sentinel data lake and the required Microsoft Defender / Sentinel Platform Services licensing enabled.
- To **create, update, or delete** custom tools, use an identity with Security Operator, Security Administrator, or Global Administrator privileges for the Microsoft Security experience plus read access to the target Sentinel workspace.
- To **list or invoke** the tools, use an identity with Security Reader or Global Reader privileges plus read access to the target Sentinel workspace.
- If API publishing is unavailable in your tenant, create the same KQL as custom tools through the Microsoft Defender portal / Advanced hunting "Save as tool" flow, then use the same runtime endpoint pattern.

## Publish the tools through the API

Clone this repo, install dependencies, and publish:

```bash
git clone https://github.com/MitchellGulledge3/upwind-sentinel-mcp-tools.git
cd upwind-sentinel-mcp-tools

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python3 scripts/publish-mcp-tools.py \
  --collection Upwind-Sentinel-MCP-Tools \
  --workspace-id "<workspace-customer-id>"
```

Use `--dry-run` first if you want to inspect the API payloads without writing anything:

```bash
python3 scripts/publish-mcp-tools.py \
  --collection Upwind-Sentinel-MCP-Tools \
  --workspace-id "<workspace-customer-id>" \
  --dry-run
```

The script is idempotent: it tolerates an existing collection and uses `PUT` for each tool, so rerunning updates the tool definitions.

## Run locally from the terminal

1. Copy environment template:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env`:
   ```text
   SENTINEL_MCP_COLLECTION=Upwind-Sentinel-MCP-Tools
   MCP_DEFAULT_ARGUMENTS={"workspaceId":"<workspace-customer-id>"}
   MCP_TOOL_ARGUMENT_TEMPLATE={}
   # Optional fallback:
   # ASSET_NAME=vm-web-prod-01
   ```

3. Ask GitHub Copilot, Claude, or another coding agent to use this repo. Suggested prompt:
   ```text
   Look at this repository and help me install and run the Upwind Sentinel custom MCP tools locally.
   Use scripts/publish-mcp-tools.py to publish the tools through the Sentinel Platform Services API,
   then use run_tools.py to call the custom MCP endpoint from this machine.
   Publish the Upwind tools and Defender Exposure tools as separate tools.
   Show how an agent can call Defender_Exposure_Asset_Context and Upwind_Asset_Risk_Investigation for the same asset.
   ```

4. Run a tool through the local terminal runner:
   ```bash
   python3 run_tools.py --prompt "Summarize Upwind cloud risk posture" --show-raw
   python3 run_tools.py --prompt "Get Defender exposure context for vm-web-prod-01" --show-raw
   python3 run_tools.py --prompt "Show Defender exposure relationships for vm-web-prod-01" --show-raw
   python3 run_tools.py --prompt "Show internet-facing critical Upwind risk" --show-raw
   python3 run_tools.py --prompt "Investigate Upwind asset vm-web-prod-01" --show-raw
   ```

The runner calls the real custom MCP endpoint at `https://sentinel.microsoft.com/mcp/custom/<collection>/` using Azure credentials. It does not use generated telemetry.

## Run locally from VS Code / GitHub Copilot

VS Code needs an MCP server registration that includes an access token for Sentinel Platform Services. Generate a short-lived config from your current Azure CLI session:

```bash
TOKEN=$(az account get-access-token \
  --resource 4500ebfb-89b6-4b14-a480-7f749797bfcd \
  --query accessToken -o tsv)

python3 scripts/write-vscode-mcp-config.py \
  --collection Upwind-Sentinel-MCP-Tools \
  --bearer-token "$TOKEN"
```

This writes `.vscode/mcp.json` with the HTTP MCP endpoint and `Authorization: Bearer <token>` header. The file is gitignored because it contains a bearer token. When the token expires, rerun the command above.

Then open `.vscode/mcp.json` in VS Code, start the MCP server from the CodeLens/command UI, and ask Copilot Chat to list or call tools from `Upwind-Sentinel-MCP-Tools`. Use prompts such as:

```text
Use the Upwind Sentinel MCP tools to summarize cloud risk posture for workspace <workspace-customer-id>.
Use Defender_Exposure_Asset_Context for asset vm-web-prod-01 in workspace <workspace-customer-id>.
Use Upwind_Asset_Risk_Investigation for asset vm-web-prod-01 in workspace <workspace-customer-id>.
Call Defender_Exposure_Asset_Context and Upwind_Asset_Risk_Investigation for vm-web-prod-01, then summarize Defender exposure context alongside Upwind runtime risk.
```

## Configure an MCP-capable agent

Register this remote MCP endpoint in any MCP-capable agent runtime that supports authenticated HTTP MCP servers:

```text
https://sentinel.microsoft.com/mcp/custom/Upwind-Sentinel-MCP-Tools/
```

At runtime, every tool requires:

```json
{
  "workspaceId": "<workspace-customer-id>"
}
```

The asset-specific Defender and Upwind tools also require:

```json
{
  "AssetName": "vm-web-prod-01"
}
```

`workspaceId` is the workspace customer ID the Sentinel custom MCP runtime uses to bind the KQL execution target. The KQL text itself does not call `workspace("<id>")`; target selection is handled by the platform tool runtime.

## Repository map

| Path | Purpose |
| --- | --- |
| `mcp-tools/*.kql` | Production-table KQL definitions published as custom MCP tools |
| `scripts/publish-mcp-tools.py` | API publisher for the Sentinel custom MCP collection |
| `scripts/write-vscode-mcp-config.py` | Writes a gitignored VS Code MCP config with a short-lived bearer token |
| `run_tools.py` | Local runner that selects a tool from a natural-language prompt and calls the custom MCP endpoint |
| `sentinel_mcp_tools/client.py` | Minimal JSON-RPC client for Sentinel custom MCP endpoints |
| `docs/tool-reference.md` | Deep explanation of every tool and how agents should use it |
| `docs/sample-output.md` | Captured/sanitized sample output from local runs |
| `docs/runbook.md` | Alpha handoff runbook for ISV and customer teams |

## Notes for alpha users

- The tools are read-only KQL tools.
- They query the last 24 hours by design.
- The Upwind tools are intentionally scoped to Upwind data and do not try to become a general CNAPP chatbot.
- Defender Exposure tools are intentionally separate from Upwind tools; agent instructions should call both when a use case needs Microsoft exposure graph context plus Upwind runtime risk.
- If a workspace has no Upwind rows in either `UpwindCatalogAssets_CL` or `UpwindLogsAssets_CL`, the tools execute but return zero-row or zero-count output.
- The tools tolerate both PascalCase and lower snake_case Upwind asset schemas where possible.
