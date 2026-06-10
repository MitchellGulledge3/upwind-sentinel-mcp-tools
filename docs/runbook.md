# Alpha Handoff Runbook

Use this when handing the repo to an Upwind ISV engineer, partner engineer, or prospect customer.

## Goal

Publish a custom Sentinel MCP collection that exposes production Upwind cloud asset risk tools, then run those tools locally from VS Code/GitHub Copilot or another MCP-capable agent surface.

## Recommended agent prompt

Paste this into GitHub Copilot, Claude, or another coding assistant after cloning the repo:

```text
Review this repository and help me install the Upwind Sentinel custom MCP tools.
Use the README as the source of truth.
Publish the tools with scripts/publish-mcp-tools.py using my Sentinel workspace customer ID.
Then run run_tools.py to call the real Sentinel custom MCP endpoint locally.
Keep the tools scoped only to Upwind tables.
```

## Step-by-step

1. Confirm production Upwind data is present:
   ```kql
   union isfuzzy=true UpwindCatalogAssets_CL, UpwindLogsAssets_CL
   | where TimeGenerated > ago(24h)
   | summarize Rows=count(), LastSeen=max(TimeGenerated)
   ```

2. Inspect the local field shape:
   ```kql
   union isfuzzy=true UpwindCatalogAssets_CL, UpwindLogsAssets_CL
   | take 5
   | project TimeGenerated, AssetName, name, CloudProvider, cloud_provider, NetworkRisk, network_risk, PublicIpAddresses, public_ip_addresses
   ```

3. Publish the collection:
   ```bash
   python3 scripts/publish-mcp-tools.py \
     --collection Upwind-Sentinel-MCP-Tools \
     --workspace-id "<workspace-customer-id>"
   ```

4. Run locally:
   ```bash
   cp .env.example .env
   # edit .env
   python3 run_tools.py --prompt "Summarize Upwind cloud risk posture" --show-raw
   python3 run_tools.py --prompt "Investigate Upwind asset vm-web-prod-01" --show-raw
   ```

5. Register the custom MCP endpoint in the consuming agent:
   ```text
   https://sentinel.microsoft.com/mcp/custom/Upwind-Sentinel-MCP-Tools/
   ```

6. For VS Code/GitHub Copilot, generate `.vscode/mcp.json`:
   ```bash
   TOKEN=$(az account get-access-token \
     --resource 4500ebfb-89b6-4b14-a480-7f749797bfcd \
     --query accessToken -o tsv)

   python3 scripts/write-vscode-mcp-config.py \
     --collection Upwind-Sentinel-MCP-Tools \
     --bearer-token "$TOKEN"
   ```

   The generated file is intentionally gitignored because it contains a short-lived bearer token.

## Common failure modes

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Tools publish but return no rows | Workspace has no Upwind rows in `UpwindCatalogAssets_CL` or `UpwindLogsAssets_CL` for the last 24h | Confirm connector ingestion and widen a manual validation query outside the tool |
| Asset investigation returns no rows | Asset/resource values are stored differently than expected | Inspect `AssetName`, `name`, `CloudResourceId`, `cloud_resource_id`, `AssetId`, and `id` |
| Risk fields are blank | Dynamic object keys differ from expected `score`, `level`, `reason`, `cve_count`, `has_kev` | Inspect raw dynamic columns and tune the KQL extraction |
| HTTP 401/403 | Azure identity cannot call Sentinel Platform Services, lacks Security Operator/Admin for publishing, lacks Security Reader for invocation, lacks workspace read access, or the tenant is not enabled for the alpha surface | Re-authenticate with `az login`; verify license, role, and workspace access |
| `workspaceId` missing | Consuming agent did not pass required argument | Include the workspace customer ID in tool arguments |

## Positioning for an ISV or customer

These are not generic chat prompts. They are product-quality tool contracts that an agent can call deterministically:

- An Upwind product agent can call them to enrich its own cloud asset risk view with Sentinel context.
- A customer Copilot can call them to triage Upwind asset risk from inside a SOC workflow.
- A partner-built agent can use them as composable primitives for cloud exposure and runtime-risk investigations.
