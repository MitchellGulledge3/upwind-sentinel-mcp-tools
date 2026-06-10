# Sample Output

Captured with `run_tools.py` calling the published `Upwind-Sentinel-MCP-Tools` custom MCP endpoint. Values are sanitized and representative of the result shapes an agent receives. The captured workspace had no production Upwind rows in `UpwindCatalogAssets_CL` or `UpwindLogsAssets_CL`, so the previews intentionally show zero-row/zero-count behavior while proving that the published tools execute successfully.

## Publish payload validation

```text
Upwind_Asset_Risk_Investigation: required=workspaceId,AssetName
Upwind_Cloud_Risk_Posture_Summary: required=workspaceId
Upwind_Detection_Risk_Triage: required=workspaceId
Upwind_High_Privilege_Risk_Hunt: required=workspaceId
Upwind_Internet_Facing_Critical_Risk: required=workspaceId
Upwind_Sensitive_Data_Exposure: required=workspaceId
Upwind_Vulnerability_Hotspots: required=workspaceId
tool_count=7
```

## `Upwind_Cloud_Risk_Posture_Summary`

Prompt: `Summarize Upwind cloud risk posture`

Arguments:

```json
{"workspaceId": "<workspace-customer-id>"}
```

Output preview:

```text
Query completed successfully, but returned no rows.

```

## `Upwind_Internet_Facing_Critical_Risk`

Prompt: `Show internet-facing critical Upwind risk`

Arguments:

```json
{"workspaceId": "<workspace-customer-id>"}
```

Output preview:

```text
Query completed successfully, but returned no rows.

```

## `Upwind_Sensitive_Data_Exposure`

Prompt: `Show Upwind sensitive data exposure`

Arguments:

```json
{"workspaceId": "<workspace-customer-id>"}
```

Output preview:

```text
Query completed successfully, but returned no rows.

```

## `Upwind_High_Privilege_Risk_Hunt`

Prompt: `Hunt high privilege Upwind risk`

Arguments:

```json
{"workspaceId": "<workspace-customer-id>"}
```

Output preview:

```text
Query completed successfully, but returned no rows.

```

## `Upwind_Vulnerability_Hotspots`

Prompt: `Show Upwind vulnerability hotspots`

Arguments:

```json
{"workspaceId": "<workspace-customer-id>"}
```

Output preview:

```text
Query completed successfully, but returned no rows.

```

## `Upwind_Detection_Risk_Triage`

Prompt: `Triage Upwind runtime detection risk`

Arguments:

```json
{"workspaceId": "<workspace-customer-id>"}
```

Output preview:

```text
Query completed successfully, but returned no rows.

```

## `Upwind_Asset_Risk_Investigation`

Prompt: `Investigate Upwind asset vm-web-prod-01`

Arguments:

```json
{"AssetName": "vm-web-prod-01", "workspaceId": "<workspace-customer-id>"}
```

Output preview:

```text
Query completed successfully, but returned no rows.

```

## Representative populated responses

The rows below are sanitized examples to show the expected shape when production Upwind data is present.

### `Upwind_Cloud_Risk_Posture_Summary`

```text
CloudProvider | Assets | CriticalRiskAssets | HighRiskAssets | InternetFacingAssets | SensitiveAtRestAssets | SensitiveInTransitAssets | UnprotectedAssets | AverageNetworkScore | AverageDetectionScore | AverageVulnerabilityScore | AveragePrivilegeScore | Categories           | ResourceTypes                                  | Accounts      | Regions
--------------+--------+--------------------+----------------+----------------------+-----------------------+--------------------------+-------------------+---------------------+-----------------------+---------------------------+-----------------------+----------------------+------------------------------------------------+---------------+---------------
aws           | 1420   | 38                 | 214            | 97                   | 83                    | 41                       | 12                | 61.2                | 28.4                  | 55.7                      | 44.9                  | ["Compute","Storage"]| ["AWS::EC2::Instance","AWS::S3::Bucket"]       | ["prod-aws"]  | ["us-east-1"]
azure         | 860    | 21                 | 96             | 54                   | 38                    | 22                       | 4                 | 58.1                | 31.9                  | 49.3                      | 47.2                  | ["Compute","Secrets"]| ["Microsoft.Compute/virtualMachines"]          | ["prod-az"]   | ["eastus"]
```

### `Upwind_Internet_Facing_Critical_Risk`

```text
AssetName      | CloudProvider | CloudAccountId | Region    | ResourceType                       | PublicIps          | NetworkLevel | DetectionLevel | VulnerabilityLevel | CombinedRiskScore
---------------+---------------+----------------+-----------+------------------------------------+--------------------+--------------+----------------+--------------------+------------------
prod-api-01    | aws           | prod-aws       | us-east-1 | AWS::EC2::Instance                 | ["203.0.113.10"]   | Critical     | High           | Critical           | 271
prod-web-vm-02 | azure         | prod-az        | eastus    | Microsoft.Compute/virtualMachines | ["203.0.113.22"]   | High         | Medium         | Critical           | 226
```

### `Upwind_Sensitive_Data_Exposure`

```text
AssetName        | CloudProvider | SensitiveTypesAtRest | SensitiveTypesInTransit | RecordsEstimate | HasPublicIp | Unprotected | NetworkLevel | VulnerabilityLevel | PrivilegeLevel | CriticalOrHighRisk
-----------------+---------------+----------------------+-------------------------+-----------------+-------------+-------------+--------------+--------------------+----------------+-------------------
payments-bucket  | aws           | PCI, PII             |                         | 4200000         | false       | false       | Medium       | High               | High           | true
customer-api-vm  | azure         | PII                  | PII                     | 980000          | true        | false       | Critical     | Critical           | Medium         | true
```

### `Upwind_High_Privilege_Risk_Hunt`

```text
AssetName       | CloudProvider | PrivilegeLevel | PrivilegeScore | PrivilegeReason                                  | HasPublicIp | NetworkLevel | VulnerabilityLevel | BlastRadiusScore
----------------+---------------+----------------+----------------+--------------------------------------------------+-------------+--------------+--------------------+-----------------
prod-runner-01  | aws           | Critical       | 95             | AdministratorAccess attached to service role     | true        | High         | High               | 150
prod-mi-api     | azure         | High           | 86             | Owner at subscription scope                      | true        | Critical     | Medium             | 126
```

### `Upwind_Vulnerability_Hotspots`

```text
CloudProvider | CloudAccountId | Region    | VulnerableAssets | CriticalAssets | HighAssets | KEVAffectedAssets | InternetFacingAssets | InternetFacingKEVAssets | TotalCVEs
--------------+----------------+-----------+------------------+----------------+------------+-------------------+----------------------+-------------------------+----------
aws           | prod-aws       | us-east-1 | 86               | 12             | 41         | 8                 | 17                   | 5                       | 1324
azure         | prod-az        | eastus    | 42               | 6              | 19         | 3                 | 9                    | 2                       | 488
```

### `Upwind_Detection_Risk_Triage`

```text
AssetName      | CloudProvider | DetectionLevel | DetectionScore | DetectionRule                         | MitreTactic       | HasPublicIp | HasSensitive | TriageTier
---------------+---------------+----------------+----------------+---------------------------------------+-------------------+-------------+--------------+--------------------
prod-api-01    | aws           | Critical       | 96             | Suspicious role assumption from ASN   | Credential Access | true        | true         | Tier-1 Containment
prod-worker-03 | azure         | High           | 82             | Unusual outbound connection           | Command Control   | false       | true         | Tier-2 Investigate
```

### `Upwind_Asset_Risk_Investigation`

```text
AssetName   | AssetId       | CloudProvider | CloudAccountId | Region    | ResourceType       | NetworkLevel | DetectionLevel | VulnerabilityLevel | PrivilegeLevel | CveCount | HasKev | HasSensitiveAtRest | AggregateRiskScore
------------+---------------+---------------+----------------+-----------+--------------------+--------------+----------------+--------------------+----------------+----------+--------+--------------------+-------------------
prod-api-01 | asset-12345   | aws           | prod-aws       | us-east-1 | AWS::EC2::Instance | Critical     | High           | Critical           | High           | 47       | true   | true               | 354
```
