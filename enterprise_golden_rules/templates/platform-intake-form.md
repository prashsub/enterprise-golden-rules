# Platform Services Intake Form
## Request for Platform Resources and Services

### Document Information
- **Request ID:** PLT-________ (assigned by Platform Team)
- **Request Date:** ________________________________
- **Requestor Name:** ________________________________
- **Requestor Team:** ________________________________
- **Requestor Email:** ________________________________
- **Priority:** [ ] Low (>2 weeks)  [ ] Medium (1-2 weeks)  [ ] High (<1 week)  [ ] Critical (immediate)

---

## Section 1: Request Type

*Select all that apply:*

### 1.1 Compute Resources
- [ ] **New SQL Warehouse** - Serverless warehouse for SQL analytics
- [ ] **SQL Warehouse Resize** - Change size or scaling parameters
- [ ] **Classic Compute Exception** - GPU, streaming, specialty libraries
- [ ] **Cluster Policy** - New or modified cluster policy

### 1.2 Data Infrastructure
- [ ] **New Catalog** - Unity Catalog creation
- [ ] **New Schema** - Schema within existing catalog
- [ ] **Volume Creation** - Unity Catalog Volume for files
- [ ] **External Location** - Cloud storage access

### 1.3 Security & Access
- [ ] **Secret Scope** - New secret scope or scope modification
- [ ] **Service Principal** - New SP for automation
- [ ] **Workspace Folder** - Shared workspace folder setup
- [ ] **Access Permissions** - Catalog/schema/table grants

### 1.4 Integration & Deployment
- [ ] **Asset Bundle Setup** - CI/CD pipeline configuration
- [ ] **Lakeflow Connect** - New data source connector
- [ ] **Network Access** - Private Link, IP access list changes
- [ ] **External Integration** - Third-party tool access

### 1.5 Monitoring & Observability
- [ ] **Lakehouse Monitor** - New monitor on Gold tables
- [ ] **SQL Alerts** - Alert configuration
- [ ] **Dashboard Access** - AI/BI Lakeview permissions

---

## Section 2: Request Details

### 2.1 Project Information

| Field | Value |
|-------|-------|
| **Project/Initiative Name** | |
| **Business Sponsor** | |
| **Expected Go-Live Date** | |
| **Environment(s)** | [ ] Dev  [ ] Staging  [ ] Production |

### 2.2 Business Justification

*Describe the business need and how this request supports it:*

_______________________________________________________________________________

_______________________________________________________________________________

_______________________________________________________________________________

### 2.3 Data Classification

*What type of data will be processed?*

- [ ] **Public** - No sensitivity, can be shared externally
- [ ] **Internal** - Business data, internal use only
- [ ] **Confidential** - Sensitive business data, restricted access
- [ ] **Restricted** - PII, PHI, financial data, regulatory requirements

*If Confidential or Restricted, specify compliance requirements:*
- [ ] GDPR
- [ ] CCPA
- [ ] HIPAA
- [ ] SOX
- [ ] PCI-DSS
- [ ] Other: ________________________________

---

## Section 3: Compute Resource Requests

*Complete this section for SQL Warehouse or compute-related requests*

### 3.1 SQL Warehouse Request

| Parameter | Value |
|-----------|-------|
| **Warehouse Name** | `[${env}]_${team}_${purpose}` |
| **Size** | [ ] 2X-Small [ ] X-Small [ ] Small [ ] Medium [ ] Large |
| **Serverless** | [ ] Yes (default) [ ] No - Justification: _____________ |
| **Auto-Stop (minutes)** | [ ] 5 [ ] 10 [ ] 15 [ ] 30 |
| **Scaling** | Min: _____ Max: _____ clusters |
| **Photon** | [ ] Enabled (default) [ ] Disabled |

**Primary Use Case:**
- [ ] Interactive SQL/BI
- [ ] Genie Spaces
- [ ] Dashboard queries
- [ ] Scheduled queries
- [ ] Other: ________________________________

**Estimated Workload:**
| Metric | Estimate |
|--------|----------|
| Queries per day | |
| Peak concurrent users | |
| Largest query (rows) | |

### 3.2 Classic Compute Exception Request

*Complete ONLY if requesting non-serverless compute*

| Field | Details |
|-------|---------|
| **Workload Type** | [ ] GPU Training [ ] 24/7 Streaming [ ] Specialty Libraries |
| **Specific Requirement** | |
| **Why Serverless Not Viable** | |
| **Duration** | [ ] Temporary (until: ____) [ ] Permanent |
| **Cost Estimate (monthly)** | $ |

*Attach: Cluster configuration YAML or screenshot*

---

## Section 4: Data Infrastructure Requests

*Complete this section for catalog, schema, or storage requests*

### 4.1 Catalog/Schema Request

| Parameter | Value |
|-----------|-------|
| **Resource Type** | [ ] Catalog [ ] Schema |
| **Name** | |
| **Parent Catalog** (for schemas) | |
| **Owner Group** | |
| **Purpose/Description** | |

**Schema Properties:**

| Property | Value |
|----------|-------|
| `layer` | [ ] bronze [ ] silver [ ] gold [ ] semantic [ ] ml [ ] monitoring |
| `domain` | |
| `data_classification` | [ ] public [ ] internal [ ] confidential [ ] restricted |
| `business_owner` | |
| `technical_owner` | |

### 4.2 Volume Request

| Parameter | Value |
|-----------|-------|
| **Volume Name** | |
| **Catalog.Schema** | |
| **Volume Type** | [ ] Managed [ ] External |
| **External Location** (if external) | |
| **Purpose** | |
| **Estimated Size (GB)** | |

### 4.3 External Location Request

| Parameter | Value |
|-----------|-------|
| **Cloud Provider** | [ ] Azure [ ] AWS [ ] GCP |
| **Storage Account/Bucket** | |
| **Container/Path** | |
| **Access Method** | [ ] Storage Credential [ ] External Location |
| **Justification** | |

---

## Section 5: Security & Access Requests

### 5.1 Secret Scope Request

| Parameter | Value |
|-----------|-------|
| **Scope Name** | `${team}-${purpose}-secrets` |
| **Backend Type** | [ ] Databricks-managed [ ] Azure Key Vault [ ] AWS Secrets Manager |
| **Key Vault URI** (if applicable) | |

**Secrets to Store:**

| Secret Key | Description | Rotates? |
|------------|-------------|----------|
| | | [ ] Yes [ ] No |
| | | [ ] Yes [ ] No |
| | | [ ] Yes [ ] No |

**Access Requirements:**

| Group | Permission Level |
|-------|------------------|
| | [ ] READ [ ] WRITE [ ] MANAGE |
| | [ ] READ [ ] WRITE [ ] MANAGE |
| | [ ] READ [ ] WRITE [ ] MANAGE |

### 5.2 Service Principal Request

| Parameter | Value |
|-----------|-------|
| **Service Principal Name** | `${project}-${purpose}-sp` |
| **Display Name** | |
| **Purpose** | |
| **Authentication** | [ ] OAuth [ ] PAT |
| **Token Expiry** | [ ] 90 days [ ] 180 days [ ] 1 year |

**Required Permissions:**

| Resource | Permission |
|----------|------------|
| Workspace | [ ] User [ ] Admin |
| Catalog(s) | |
| Schema(s) | |
| Secret Scope(s) | |

### 5.3 Workspace Folder Request

| Parameter | Value |
|-----------|-------|
| **Folder Path** | `/Shared/${team}/${project}` |
| **Purpose** | |

**Folder Permissions:**

| Group | Permission |
|-------|------------|
| | [ ] CAN_READ [ ] CAN_RUN [ ] CAN_EDIT [ ] CAN_MANAGE |
| | [ ] CAN_READ [ ] CAN_RUN [ ] CAN_EDIT [ ] CAN_MANAGE |

### 5.4 Catalog/Schema Access Request

| Resource | Group | Permission |
|----------|-------|------------|
| | | [ ] USE_CATALOG [ ] USE_SCHEMA [ ] SELECT [ ] MODIFY [ ] ALL PRIVILEGES |
| | | [ ] USE_CATALOG [ ] USE_SCHEMA [ ] SELECT [ ] MODIFY [ ] ALL PRIVILEGES |
| | | [ ] USE_CATALOG [ ] USE_SCHEMA [ ] SELECT [ ] MODIFY [ ] ALL PRIVILEGES |

---

## Section 6: Integration & Deployment Requests

### 6.1 Asset Bundle Setup

| Parameter | Value |
|-----------|-------|
| **Git Repository URL** | |
| **Default Branch** | |
| **Target Environments** | [ ] Dev [ ] Staging [ ] Production |
| **Deployment Trigger** | [ ] Manual [ ] On Push [ ] Scheduled |

**Resources to Deploy:**

- [ ] Jobs
- [ ] Pipelines (DLT)
- [ ] SQL Warehouses
- [ ] Schemas
- [ ] Functions
- [ ] Dashboards

### 6.2 Lakeflow Connect Request

| Parameter | Value |
|-----------|-------|
| **Source System** | [ ] Salesforce [ ] ServiceNow [ ] SQL Server [ ] Workday [ ] Other: _____ |
| **Source Details** | |
| **Target Catalog.Schema** | |
| **Sync Frequency** | [ ] Real-time [ ] Hourly [ ] Daily |
| **Estimated Volume** | |

### 6.3 Network Access Request

| Parameter | Value |
|-----------|-------|
| **Request Type** | [ ] Private Link [ ] IP Access List [ ] VNet Peering |
| **Source Network/IP** | |
| **Destination** | |
| **Protocol/Port** | |
| **Business Justification** | |

*Attach: Network diagram if complex*

---

## Section 7: Monitoring & Observability Requests

### 7.1 Lakehouse Monitor Request

| Parameter | Value |
|-----------|-------|
| **Table to Monitor** | `catalog.schema.table` |
| **Monitor Type** | [ ] Snapshot [ ] TimeSeries |
| **Granularity** (if time series) | |
| **Schedule** | [ ] Daily [ ] Weekly [ ] Monthly |

**Custom Metrics Required:**

| Metric Name | Type | Expression |
|-------------|------|------------|
| | [ ] AGGREGATE [ ] DERIVED | |
| | [ ] AGGREGATE [ ] DERIVED | |

### 7.2 SQL Alert Request

| Parameter | Value |
|-----------|-------|
| **Alert Name** | |
| **Query/Condition** | |
| **Threshold** | |
| **Notification** | [ ] Email [ ] Slack [ ] PagerDuty |
| **Recipients** | |

---

## Section 8: Cost & Capacity

### 8.1 Estimated Resource Usage

| Resource | Estimate | Period |
|----------|----------|--------|
| SQL Warehouse DBUs | | per day |
| Job Compute DBUs | | per day |
| DLT Pipeline DBUs | | per day |
| Storage (GB) | | total |

### 8.2 Cost Center

| Field | Value |
|-------|-------|
| **Cost Center** | |
| **Budget Approved** | [ ] Yes [ ] Pending |
| **Budget Owner** | |

---

## Section 9: Technical Specifications

*Attach or describe additional technical details:*

### 9.1 Architecture Diagram
- [ ] Attached
- [ ] Not applicable
- [ ] Will be provided by: ___/___/______

### 9.2 Data Flow
- [ ] Attached
- [ ] Not applicable
- [ ] Will be provided by: ___/___/______

### 9.3 ERD/Schema Design
- [ ] Attached
- [ ] Not applicable
- [ ] Will be provided by: ___/___/______

---

## Section 10: Dependencies & Constraints

### 10.1 Dependencies

| Dependency | Status | Owner |
|------------|--------|-------|
| | [ ] Ready [ ] In Progress [ ] Blocked | |
| | [ ] Ready [ ] In Progress [ ] Blocked | |
| | [ ] Ready [ ] In Progress [ ] Blocked | |

### 10.2 Known Constraints

_______________________________________________________________________________

_______________________________________________________________________________

---

## Section 11: Golden Rules Compliance

*Platform Team will verify compliance with these rules:*

| Rule | Compliance | Notes |
|------|------------|-------|
| **DL-01** Unity Catalog (no HMS) | [ ] Compliant [ ] Exception Needed | |
| **DL-04** Delta Lake format | [ ] Compliant [ ] Exception Needed | |
| **SC-01** Serverless compute | [ ] Compliant [ ] Exception Needed | |
| **IN-01** Asset Bundles | [ ] Compliant [ ] Exception Needed | |
| **SM-01** Secrets in scopes | [ ] Compliant [ ] Exception Needed | |

*If exception needed, attach Exception Request Form*

---

## Section 12: Approvals & Workflow

### 12.1 Required Approvals

| Role | Required For | Status |
|------|--------------|--------|
| **Requestor Manager** | All requests | [ ] Pending [ ] Approved |
| **Data Steward** | Catalog/schema creation | [ ] Pending [ ] Approved [ ] N/A |
| **Security Team** | Secret scopes, network, SPs | [ ] Pending [ ] Approved [ ] N/A |
| **Platform Team** | All requests (final) | [ ] Pending [ ] Approved |
| **Cost Center Owner** | High-cost resources | [ ] Pending [ ] Approved [ ] N/A |

### 12.2 Approval Signatures

| Approver | Name | Decision | Date |
|----------|------|----------|------|
| Manager | | [ ] Approve [ ] Deny | |
| Data Steward | | [ ] Approve [ ] Deny [ ] N/A | |
| Security | | [ ] Approve [ ] Deny [ ] N/A | |
| Platform Team | | [ ] Approve [ ] Deny | |

---

## Section 13: Requestor Certification

I certify that:
- [ ] The information provided is accurate and complete
- [ ] I have reviewed the Platform Architecture standards
- [ ] I understand serverless is the default for all compute
- [ ] I commit to following Golden Rules for all resources
- [ ] I will notify the Platform Team of any scope changes

**Requestor Signature:** ________________________________

**Date:** ________________________________

---

## Office Use Only

| Field | Value |
|-------|-------|
| **Request ID** | PLT-________ |
| **Received Date** | |
| **Assigned To** | |
| **Priority** | [ ] Low [ ] Medium [ ] High [ ] Critical |
| **Target Completion** | |
| **Status** | [ ] New [ ] In Progress [ ] Completed [ ] On Hold [ ] Cancelled |
| **Completion Date** | |
| **Notes** | |

### Implementation Checklist

- [ ] Resources created in Dev
- [ ] Resources tested in Dev
- [ ] Resources created in Staging (if applicable)
- [ ] Resources created in Production
- [ ] Access grants applied
- [ ] Documentation updated
- [ ] Requestor notified
- [ ] Request closed

---

## Submission Instructions

1. **Complete all relevant sections** of this form
2. **Attach supporting documents** (architecture diagrams, ERDs, YAML configs)
3. **Obtain manager approval** before submission
4. **Submit via:**
   - **ServiceNow:** Create "Platform Request" ticket
   - **Email:** platform-requests@company.com
   - **Slack:** #platform-requests channel
5. **Expected Response Times:**
   - Low priority: 10 business days
   - Medium priority: 5 business days
   - High priority: 2 business days
   - Critical: Same day (requires escalation approval)

---

## Frequently Asked Questions

**Q: Do I need a separate form for each resource?**
A: No, you can request multiple related resources on one form. For unrelated requests, submit separate forms.

**Q: How do I request an exception to serverless compute?**
A: Select "Classic Compute Exception" and complete Section 3.2. For formal exceptions, also submit the Exception Request Form.

**Q: Who approves secret scope requests?**
A: All secret scope requests require Security Team approval in addition to Platform Team.

**Q: Can I request resources for multiple environments at once?**
A: Yes, select all applicable environments in Section 2.1. Resources will be created following our promotion process (Dev → Staging → Prod).

**Q: What if my request is urgent?**
A: Mark priority as "Critical" and contact the Platform Team directly via Slack. Critical requests require manager + Platform Lead approval.

**Q: How do I track my request status?**
A: Use the Request ID (PLT-XXXXX) to query status in ServiceNow or contact platform-requests@company.com.

---

## Related Documents

- [Platform Architecture Overview](../platform-architecture/10-platform-overview.md)
- [Serverless Compute Standards](../platform-architecture/11-serverless-compute.md)
- [Unity Catalog Tables](../platform-architecture/12-unity-catalog-tables.md)
- [Secrets Management](../platform-architecture/14-secrets-workspace-management.md)
- [Asset Bundle Standards](../platform-architecture/19-asset-bundle-standards.md)
- [Exception Request Form](exception-request-form.md)
- [Architecture Review Checklist](architecture-review-checklist.md)

---

*Platform Intake Form Version 1.0 - Based on Enterprise Golden Rules*
