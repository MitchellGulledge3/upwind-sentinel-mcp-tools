# Sample Output

Captured with `run_tools.py` calling the published `Upwind-Sentinel-MCP-Tools` custom MCP endpoint. Values are sanitized and representative of the result shapes an agent receives. The captured workspace had no production Upwind rows in `UpwindCatalogAssets_CL` / `UpwindLogsAssets_CL` and no Defender Exposure graph rows, so the live previews intentionally show zero-row behavior while proving that the published tools execute successfully.

## Publish payload validation

```text
Defender_Exposure_Asset_Context: required=workspaceId,AssetName
Defender_Exposure_Asset_Relationships: required=workspaceId,AssetName
Upwind_Asset_Risk_Investigation: required=workspaceId,AssetName
Upwind_Cloud_Risk_Posture_Summary: required=workspaceId
Upwind_Detection_Risk_Triage: required=workspaceId
Upwind_High_Privilege_Risk_Hunt: required=workspaceId
Upwind_Internet_Facing_Critical_Risk: required=workspaceId
Upwind_Sensitive_Data_Exposure: required=workspaceId
Upwind_Vulnerability_Hotspots: required=workspaceId
tool_count=9
```

## Live execution previews

### `Defender_Exposure_Asset_Context`

Prompt: `Get Defender exposure context for vm-web-prod-01`

Arguments:

```json
{"AssetName": "vm-web-prod-01", "workspaceId": "<workspace-customer-id>"}
```

Output preview:

```text
Query completed successfully, but returned no rows.

```

### `Defender_Exposure_Asset_Relationships`

Prompt: `Show Defender exposure relationships for vm-web-prod-01`

Arguments:

```json
{"AssetName": "vm-web-prod-01", "workspaceId": "<workspace-customer-id>"}
```

Output preview:

```text
Query completed successfully, but returned no rows.

```

### `Upwind_Asset_Risk_Investigation`

Prompt: `Investigate Upwind asset vm-web-prod-01`

Arguments:

```json
{"AssetName": "vm-web-prod-01", "workspaceId": "<workspace-customer-id>"}
```

Output preview:

```text
Query completed successfully, but returned no rows.

```

### `Upwind_Cloud_Risk_Posture_Summary`

Prompt: `Summarize Upwind cloud risk posture`

Arguments:

```json
{"workspaceId": "<workspace-customer-id>"}
```

Output preview:

```text
Query completed successfully, but returned no rows.

```

## Representative populated responses

The rows below are sanitized examples to show the expected shape when production Defender Exposure and Upwind data are present.

### `Defender_Exposure_Asset_Context`

```text
NodeId       | NodeName       | NodeLabel       | Categories                         | EntityIds                         | NodeProperties
-------------+----------------+-----------------+------------------------------------+-----------------------------------+------------------------------------------------------------
node-vm-001  | vm-web-prod-01 | virtual machine | ["cloud asset","compute"]       | {"azureResourceId":"/.../vm"}  | {"isInternetFacing":true,"riskLevel":"High"}
```

### `Defender_Exposure_Asset_Relationships`

```text
MatchedNodeName | MatchedNodeLabel | EdgeDirection | EdgeLabel           | RelatedNodeName       | RelatedNodeLabel | RelatedNodeCategories       | EdgeProperties
----------------+------------------+---------------+---------------------+-----------------------+------------------+-----------------------------+----------------------------
vm-web-prod-01  | virtual machine  | outbound      | can access          | prod-keyvault-01      | key vault        | ["secret store"]           | {"pathType":"attackPath"}
vm-web-prod-01  | virtual machine  | inbound       | exposed from        | internet              | external entity  | ["internet"]               | {"port":"443"}
```

### `Upwind_Asset_Risk_Investigation`

```text
AssetName      | AssetId     | CloudProvider | CloudAccountId | Region  | ResourceType                       | NetworkLevel | DetectionLevel | VulnerabilityLevel | PrivilegeLevel | CveCount | HasKev | HasSensitiveAtRest | AggregateRiskScore
---------------+-------------+---------------+----------------+---------+------------------------------------+--------------+----------------+--------------------+----------------+----------+--------+--------------------+-------------------
vm-web-prod-01 | asset-12345 | azure         | prod-az        | eastus  | Microsoft.Compute/virtualMachines | Critical     | High           | Critical           | High           | 47       | true   | true               | 354
```

### Combined agent answer pattern

```text
Defender Exposure shows vm-web-prod-01 is internet-facing and connected to a key vault through an attack-path edge. Upwind shows the same asset has Critical network risk, High runtime detection risk, Critical vulnerability risk with KEV exposure, High privilege risk, and sensitive data at rest. Recommended priority: restrict public exposure first, isolate or investigate active runtime detections, rotate/restrict key vault access, and patch KEV vulnerabilities.
```
