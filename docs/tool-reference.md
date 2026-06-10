# Upwind Custom MCP Tool Reference

These tools are designed for agents that need precise, callable Sentinel capabilities over production Upwind cloud asset risk data. Each tool is a Kqs tool published through the Sentinel Platform Services custom MCP API.

## Shared design choices

- **Primary tables:** `UpwindCatalogAssets_CL` and `UpwindLogsAssets_CL`.
- **Scope:** Upwind tools query Upwind tables only. Defender tools query Exposure Management tables only. The consuming agent correlates outputs by invoking both.
- **Defender Exposure tables:** `ExposureGraphNodes` and `ExposureGraphEdges`.
- **Schema compatibility:** tools normalize PascalCase fields (`AssetName`, `CloudProvider`, `NetworkRisk`) and lower snake_case fields (`name`, `cloud_provider`, `network_risk`).
- **Dynamic risk objects:** tools read risk levels and scores from `NetworkRisk`, `DetectionRisk`, `VulnerabilityRisk`, `HighPrivilegeRisk`, `SensitiveDataAtRest`, and `SensitiveDataInTransit`.
- **Missing-table behavior:** tools use `union isfuzzy=true` source aliases so alpha customers can publish/run them before every Upwind table is present.
- **Migration caveat:** if both `UpwindCatalogAssets_CL` and `UpwindLogsAssets_CL` are populated, aggregate tools may count the same asset from both tables.
- **Nested keys:** dynamic sub-property names such as `score`, `level`, `cve_count`, `has_kev`, `mitre_tactic`, `mitre_technique`, `rule`, `reason`, `has_sensitive_data`, and `types` should be confirmed against a real row in the target workspace.
- **Authentication:** the consuming agent authenticates to Sentinel MCP; the tools themselves are read-only KQL.
- **Workspace binding:** every tool requires `workspaceId`. The Sentinel custom MCP runtime uses that argument to bind the KQL execution target; the KQL files do not call `workspace("<id>")` directly.
- **Parameter syntax:** Kqs tools use single-brace placeholders such as `{AssetName}` in `queryFormat`. The publisher detects those placeholders and declares matching tool arguments.

## `Upwind_Cloud_Risk_Posture_Summary`

**Question answered:** "What is our Upwind cloud asset risk posture in the last 24 hours?"

**What it does:**

1. Counts assets by cloud provider.
2. Counts critical/high assets across network, detection, vulnerability, and privilege risk.
3. Counts internet-facing assets, sensitive-data assets, and unprotected assets.
4. Summarizes average risk scores, categories, resource types, accounts, and regions.

**Best caller prompt:** "Summarize Upwind cloud risk posture."

## `Defender_Exposure_Asset_Context`

**Question answered:** "What does Microsoft Security Exposure Management know about this asset/entity?"

**Required arguments:**

```json
{
  "workspaceId": "<workspace-customer-id>",
  "AssetName": "vm-web-prod-01"
}
```

**What it does:**

1. Searches `ExposureGraphNodes` by node name, entity IDs, and node properties.
2. Returns node ID, name, label, categories, entity IDs, and raw node properties.
3. Gives an agent the Defender Exposure node context for a later Upwind lookup.

**Best caller prompt:** "Get Defender exposure context for vm-web-prod-01."

## `Defender_Exposure_Asset_Relationships`

**Question answered:** "What graph relationships and nearby attack-path context surround this asset/entity?"

**Required arguments:**

```json
{
  "workspaceId": "<workspace-customer-id>",
  "AssetName": "vm-web-prod-01"
}
```

**What it does:**

1. Finds matching nodes in `ExposureGraphNodes`.
2. Joins direct inbound and outbound edges from `ExposureGraphEdges`.
3. Returns relationship direction, edge label, related node name/label/categories, and edge properties.

**Best caller prompt:** "Show Defender exposure relationships for vm-web-prod-01."

## Combined Defender + Upwind workflow

For an asset-level investigation, call these tools separately:

1. `Defender_Exposure_Asset_Context`
2. `Defender_Exposure_Asset_Relationships`
3. `Upwind_Asset_Risk_Investigation`

Then have the consuming agent produce one response that clearly separates:

- **Defender Exposure evidence:** graph node identity, categories, properties, and relationships.
- **Upwind evidence:** runtime detections, vulnerabilities, high privilege, internet exposure, sensitive data, public/private IPs, technologies, and aggregate risk score.
- **Recommended remediation:** network exposure reduction, privilege reduction, patch/KEV action, sensitive-data protection, and runtime containment if needed.

## `Upwind_Internet_Facing_Critical_Risk`

**Question answered:** "Which public-facing assets have critical/high Upwind risk?"

**What it does:**

1. Filters assets with public IPs.
2. Keeps assets with critical/high network, detection, or vulnerability risk.
3. Projects asset name, provider, account, region, resource type, public IPs, technologies, risk levels, and combined score.

**Best caller prompt:** "Show internet-facing critical Upwind risk."

## `Upwind_Sensitive_Data_Exposure`

**Question answered:** "Which Upwind assets contain sensitive data and have meaningful risk context?"

**What it does:**

1. Finds assets with sensitive data at rest or in transit.
2. Adds public exposure, protection, network, detection, vulnerability, and privilege context.
3. Ranks sensitive assets with high/critical risk first.

**Best caller prompt:** "Show Upwind sensitive data exposure."

## `Upwind_High_Privilege_Risk_Hunt`

**Question answered:** "Which assets have high privilege blast radius?"

**What it does:**

1. Filters assets with high or critical privilege risk.
2. Adds public exposure, network risk, and vulnerability context.
3. Computes a blast-radius score.

**Best caller prompt:** "Hunt high privilege Upwind risk."

## `Upwind_Vulnerability_Hotspots`

**Question answered:** "Where are the worst Upwind vulnerability concentrations?"

**What it does:**

1. Groups vulnerable assets by provider, account, and region.
2. Counts critical/high/medium assets, KEV-affected assets, internet-facing assets, internet-facing KEV assets, and total CVEs.
3. Includes example assets, technologies, and resource types.

**Best caller prompt:** "Show Upwind vulnerability hotspots."

## `Upwind_Detection_Risk_Triage`

**Question answered:** "Which runtime detections need containment or investigation first?"

**What it does:**

1. Finds assets with critical/high/medium detection risk.
2. Extracts detection score, rule, MITRE tactic, and MITRE technique.
3. Adds public exposure and sensitive-data context.
4. Assigns a triage tier.

**Best caller prompt:** "Triage Upwind runtime detection risk."

## `Upwind_Asset_Risk_Investigation`

**Question answered:** "What is the complete Upwind risk profile for this asset?"

**Required arguments:**

```json
{
  "workspaceId": "<workspace-customer-id>",
  "AssetName": "vm-web-prod-01"
}
```

**What it does:**

1. Matches the supplied value against asset name, asset ID, or cloud resource ID.
2. Returns identity, cloud, resource, tag, IP, technology, network, detection, vulnerability, privilege, and sensitive-data context.
3. Computes an aggregate risk score from Upwind-only signals.

**Best caller prompt:** "Investigate Upwind asset vm-web-prod-01."
