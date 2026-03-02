# Network Security Golden Rules
**Rules:** SEC-01..09, SM-01..04 | **Count:** 13 | **Version:** 5.4.0

## Rules Summary
| ID | Rule | Severity | Quick Check |
|----|------|----------|-------------|
| SEC-01 | Production workspaces must use VNet/VPC injection | Critical | Compute deploys into customer-managed VNet/VPC |
| SEC-02 | Configure Private Link/PSC for control plane access | Critical | Workspace resolves to private IP, not public |
| SEC-03 | Implement IP access lists for workspace access | Required | IP allow-list configured per environment |
| SEC-04 | Use customer-managed keys (CMK) for encryption | Required | Key Vault / KMS / Cloud KMS configured |
| SEC-05 | Enable diagnostic logging to cloud monitoring | Critical | Log categories flowing to monitoring service |
| SEC-06 | Configure network egress controls | Required | Firewall rules restrict outbound traffic |
| SEC-07 | Use secure cluster connectivity (no public IPs) | Critical | Cluster nodes have no public IP addresses |
| SEC-08 | Enable Compliance Security Profile for regulated workloads | Required | Profile active for HIPAA/PCI/FedRAMP workspaces |
| SEC-09 | Security monitoring and SIEM integration | Required | Audit logs forwarded to enterprise SIEM |
| SM-01 | All secrets in Databricks Secret Scopes | Critical | No plaintext secrets in code |
| SM-02 | Never hardcode credentials | Critical | No passwords/tokens in source |
| SM-03 | Use dbutils.secrets.get() only | Required | No env vars for secrets |
| SM-04 | Workspace follows naming conventions | Required | Standard naming applied |

## Detailed Rules

### SEC-01: VNet/VPC Injection
**Severity:** Critical | **Trigger:** When provisioning any production workspace

**Rule:** All production workspaces must deploy compute resources into customer-managed virtual networks (Azure VNet, AWS VPC, or GCP VPC).
**Why:** Without VNet injection, cluster nodes run in Databricks-managed networks with no visibility into traffic routing, no integration with corporate firewalls, and no ability to enforce custom security group rules.

**Correct:**
```
Customer VNet / VPC
+-- public-subnet (NAT gateway)
|   +-- Databricks control plane connectivity
+-- private-subnet (worker nodes)
|   +-- Cluster compute resources
+-- Security Groups (NSG / AWS SG / GCP Firewall Rules)
    +-- Ingress/egress rules
```

Required subnet sizing:

| Subnet | CIDR (minimum) | Purpose |
|--------|----------------|---------|
| Public | /26 (64 IPs) | Control plane connectivity |
| Private | /26 (64 IPs) | Worker nodes |

**Anti-Pattern:**
```
# WRONG: Default Databricks-managed networking
# No VNet injection configured at workspace creation
# Result: No control over network security, no firewall integration
```

---

### SEC-02: Private Link / Private Service Connect
**Severity:** Critical | **Trigger:** When configuring workspace network access

**Rule:** Configure private connectivity endpoints (Azure Private Link, AWS PrivateLink, or GCP PSC) to eliminate public internet transit for control plane access.
**Why:** Without Private Link, all management API calls, notebook interactions, and workspace UI traffic traverse the public internet, exposing metadata and credentials to potential interception.

**Correct:**
```
User Network
    |
    +-- Private Endpoint / Interface Endpoint / PSC Endpoint
            |
            +-- Private Link (Azure) / PrivateLink (AWS) / PSC (GCP)
                    |
                    +-- Databricks Control Plane (private)
```

Verification:
```bash
# Test private endpoint resolution
nslookup myworkspace.azuredatabricks.net    # Azure
nslookup myworkspace.cloud.databricks.com   # AWS / GCP
# Should resolve to private IP (10.x.x.x), not public
```

**Anti-Pattern:**
```bash
# WRONG: Public access still enabled
nslookup myworkspace.azuredatabricks.net
# Resolves to public IP (52.x.x.x) -- control plane exposed
```

---

### SEC-03: IP Access Lists
**Severity:** Required | **Trigger:** When hardening workspace access beyond authentication

**Rule:** Configure IP access lists to restrict workspace access to known trusted networks (corporate VPN, CI/CD runners).
**Why:** IP access lists provide a network-layer defense even if credentials are compromised, limiting the blast radius of token theft or phishing attacks.

**Correct:**
```json
{
  "ip_access_lists": [
    {
      "label": "Corporate VPN",
      "list_type": "ALLOW",
      "ip_addresses": ["10.0.0.0/8", "172.16.0.0/12"]
    },
    {
      "label": "Known Threats",
      "list_type": "BLOCK",
      "ip_addresses": ["192.168.100.0/24"]
    }
  ]
}
```

Environment policies:

| Environment | IP Access Policy |
|-------------|------------------|
| Production | Corporate VPN + known IPs only |
| Staging | Corporate VPN + CI/CD runners |
| Development | Corporate VPN (broader range) |

**Anti-Pattern:**
```json
{
  "ip_access_lists": []
}
```

---

### SEC-04: Customer-Managed Keys (CMK)
**Severity:** Required | **Trigger:** When provisioning workspaces for regulated or sensitive data

**Rule:** Use customer-managed keys for workspace encryption via your cloud's key management service (Azure Key Vault, AWS KMS, or GCP Cloud KMS).
**Why:** CMK provides full control over the encryption key lifecycle, enables key revocation to render data unreadable, and satisfies FIPS 140-2 compliance requirements.

**Correct:**

| Setting | Azure Key Vault | AWS KMS | GCP Cloud KMS |
|---------|----------------|---------|---------------|
| Deletion protection | Soft delete + purge protection | Key deletion pending period | Destroy protection |
| Key type | RSA 2048+ | Symmetric or RSA | Symmetric or RSA |
| Permissions | Get, Wrap, Unwrap | Encrypt, Decrypt, GenerateDataKey | Encrypt, Decrypt |

Implementation steps:
1. Create key store with appropriate protection level
2. Generate or import encryption key (RSA 2048 minimum)
3. Configure key rotation policy (recommended: annual)
4. Enable CMK for workspace during creation or migration

**Anti-Pattern:**
```
# WRONG: Relying solely on platform-managed keys
# No Key Vault / KMS configured
# No key rotation policy
# No deletion protection enabled
```

---

### SEC-05: Diagnostic Logging
**Severity:** Critical | **Trigger:** When any workspace is created or reviewed

**Rule:** Enable diagnostic logging to your cloud monitoring service for all security-relevant event categories.
**Why:** Without centralized logging, security incidents go undetected, compliance audits lack evidence, and operational issues require manual workspace-by-workspace investigation.

**Correct:**

Required log categories:

| Category | Description |
|----------|-------------|
| dbfs | DBFS operations |
| clusters | Cluster lifecycle events |
| accounts | User and group management |
| jobs | Job execution events |
| notebook | Notebook operations |
| workspace | Workspace configuration events |
| unityCatalog | Data governance events |

| Cloud | Monitoring Service | Configuration |
|-------|-------------------|---------------|
| Azure | Azure Monitor / Log Analytics | Diagnostic settings on workspace resource |
| AWS | CloudWatch / S3 delivery | Log delivery configuration in account console |
| GCP | Cloud Logging / BigQuery | Audit log configuration |

**Anti-Pattern:**
```
# WRONG: Logging disabled or only partial categories enabled
# Result: Security events invisible, compliance gaps, no forensic trail
```

---

### SEC-06: Network Egress Controls
**Severity:** Required | **Trigger:** When configuring VNet/VPC firewall rules

**Rule:** Implement network egress controls to prevent unauthorized data exfiltration by restricting outbound traffic to approved destinations only.
**Why:** Without egress controls, compromised code or malicious insiders can exfiltrate data to arbitrary external endpoints without detection.

**Correct:**
```
Allow:
+-- Cloud storage (blob.core.windows.net / s3.amazonaws.com / storage.googleapis.com)
+-- Databricks services (*.azuredatabricks.net / *.cloud.databricks.com)
+-- PyPI/Maven (package managers)
+-- Corporate services (specific IPs)

Deny:
+-- All other outbound traffic
```

Implementation options by cloud:

| Azure | AWS | GCP |
|-------|-----|-----|
| Azure Firewall | AWS Network Firewall | GCP Cloud Firewall |
| NSG rules | Security Groups | Firewall Rules |
| NAT Gateway | NAT Gateway | Cloud NAT |
| UDRs | Route Tables | Custom Routes |

**Anti-Pattern:**
```
# WRONG: Default allow-all egress
# Outbound security group: 0.0.0.0/0 ALLOW ALL
# Result: Any code can send data to any internet destination
```

---

### SEC-07: Secure Cluster Connectivity (No Public IPs)
**Severity:** Critical | **Trigger:** When deploying any production cluster

**Rule:** Enable secure cluster connectivity so that cluster nodes have no public IP addresses; all traffic flows through the control plane tunnel.
**Why:** Public IPs on cluster nodes create a direct attack surface from the internet, bypass corporate firewall policies, and violate zero-trust network principles.

**Correct:**
```sql
-- Verify cluster configuration via system tables
SELECT cluster_id, cluster_name,
       single_user_name,
       data_security_mode
FROM system.compute.clusters
WHERE enable_elastic_disk = true;
```

Requirements:
- VNet injection enabled (SEC-01)
- Outbound connectivity to control plane via NAT gateway
- Private Link or secure tunnel for management traffic

**Anti-Pattern:**
```
# WRONG: Clusters with public IP addresses
# enable_public_ip: true (or not explicitly disabled)
# Result: Cluster nodes directly reachable from internet
```

---

### SEC-08: Compliance Security Profile
**Severity:** Required | **Trigger:** When workspace processes HIPAA, PCI-DSS, FedRAMP, or SOC 2 regulated data

**Rule:** Enable the Compliance Security Profile for all workspaces processing regulated workloads to activate automatic security hardening, CIS-benchmark compute images, and enhanced monitoring.
**Why:** Regulated industries require specific security controls (image hardening, automatic patching, enhanced audit) that are only available through the Compliance Security Profile add-on.

**Correct:**

| Regulation | Industries | Profile Setting |
|------------|-----------|-----------------|
| HIPAA | Healthcare, health insurance | Compliance Security Profile |
| PCI-DSS | Payment processing, financial services | Compliance Security Profile |
| FedRAMP | US government contractors | Compliance Security Profile + IL4/IL5 |
| SOC 2 Type II | Any organization in audit scope | Compliance Security Profile |

What it provides:

| Capability | Description |
|------------|-------------|
| Image hardening | CIS benchmark-compliant compute images |
| Automatic patching | Security updates applied without disruption |
| Enhanced monitoring | Additional audit and compliance logging |
| Network controls | Stricter default network configurations |

**Anti-Pattern:**
```
# WRONG: Processing HIPAA data without Compliance Security Profile
# Standard workspace with default security controls
# Result: Missing required security hardening, audit gaps, compliance violation
```

---

### SEC-09: SIEM Integration
**Severity:** Required | **Trigger:** When establishing production security monitoring

**Rule:** All production workspaces must forward audit logs and security events to the organization's SIEM system for centralized security monitoring and incident correlation.
**Why:** Without SIEM integration, Databricks security events are siloed from enterprise threat detection, preventing correlation with network, endpoint, and application security signals.

**Correct:**
```sql
-- Streaming pipeline to export security events to SIEM
CREATE OR REFRESH STREAMING TABLE security_events AS
SELECT
    event_time,
    service_name,
    action_name,
    identity.email AS user_email,
    source_ip_address,
    request_params
FROM STREAM(system.access.audit)
WHERE action_name IN (
    'createCluster', 'deleteCluster',
    'changePermissions', 'login', 'tokenLogin'
);
```

Integration paths by cloud:

| Cloud | Log Source | SIEM Integration |
|-------|-----------|------------------|
| Azure | Diagnostic Settings | Azure Sentinel, Splunk via Event Hub |
| AWS | System tables audit logs | Splunk, Datadog via S3/Kinesis |
| GCP | System tables audit logs | Chronicle, Splunk via Pub/Sub |

**Anti-Pattern:**
```
# WRONG: Audit logs only in system.access.audit with no forwarding
# Result: No correlation with enterprise security events
# No automated alerting on suspicious activity
```

---

## Quick Reference
```bash
# Check workspace network configuration (Azure)
az databricks workspace show --name myworkspace -g mygroup \
  --query "{vnet:parameters.customVirtualNetworkId.value, \
            privateLink:privateEndpointConnections}"

# List IP access lists
databricks ip-access-lists list

# Check diagnostic settings (Azure)
az monitor diagnostic-settings list \
  --resource /subscriptions/.../workspaces/myworkspace
```

---

## Checklist
- [ ] SEC-01: VNet/VPC injection configured for all production workspaces
- [ ] SEC-02: Private Link/PSC enabled; workspace resolves to private IP
- [ ] SEC-03: IP access lists restrict access to corporate VPN and CI/CD
- [ ] SEC-04: Customer-managed keys configured with rotation policy
- [ ] SEC-05: All seven diagnostic log categories flowing to monitoring
- [ ] SEC-06: Egress firewall rules deny all except approved destinations
- [ ] SEC-07: Secure cluster connectivity enabled (no public IPs on nodes)
- [ ] SEC-08: Compliance Security Profile active for regulated workspaces
- [ ] SEC-09: Audit logs forwarded to enterprise SIEM with alerting rules
- [ ] SM-01: All secrets stored in Databricks Secret Scopes
- [ ] SM-02: No hardcoded credentials in any code or config
- [ ] SM-03: Secrets accessed via dbutils.secrets.get() only
- [ ] SM-04: Workspace naming follows organizational standards
