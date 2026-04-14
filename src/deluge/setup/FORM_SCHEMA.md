# Zoho Creator Form Schema

Create these 6 forms **in this order** before running `install_app.dg`.

---

## Contents

- [Role Permissions](#role-permissions)
- [Forms](#forms)
  - [1. regional_config](#1-regional_config)
  - [2. dispute_reason_codes](#2-dispute_reason_codes)
  - [3. chargeback_incidents](#3-chargeback_incidents)
  - [4. dispute_submissions](#4-dispute_submissions)
  - [5. audit_trail](#5-audit_trail)
  - [6. file_uploads](#6-file_uploads)
- [Workflow Scripts](#workflow-scripts)
  - [Form Workflows](#form-workflows)
  - [Scheduled Tasks](#scheduled-tasks)
  - [Custom APIs](#custom-apis)
  - [Setup](#setup)

---

## Role Permissions

Three roles interact with the application. Configure Zoho Creator permissions to match the access model below.

| Role | Forms: Read | Forms: Write | Reports | Custom APIs | Notifications |
|------|-------------|-------------|---------|-------------|---------------|
| **Credit Controller** | All forms | chargeback_incidents, dispute_submissions, file_uploads | All reports | get_dashboard_summary, get_aging_report | Dispute submitted, file processing, data cleansing |
| **Lifestyle Manager** | chargeback_incidents (assigned only), dispute_submissions | dispute_submissions (own records) | Open Chargebacks, Expiring Soon | None | New chargeback assigned, deadline warning, expiry |
| **CFO / COO** | All forms (read-only) | None | All reports | get_dashboard_summary, get_aging_report | Escalation (expired chargebacks, critical deadlines) |

**How to configure in Zoho Creator:**

1. Go to **Settings > Users and Roles > Roles**
2. Create three roles: `Credit Controller`, `Lifestyle Manager`, `CFO`
3. For each role, set form-level permissions under **Settings > Users and Roles > Permissions**
4. Restrict Lifestyle Manager access to assigned records using the criteria: `Assigned_LM == zoho.loginuser`

**System-level access:** Scheduled tasks and audit trail entries run as `zoho.adminuser`. The `Added_User` field on every insert operation tracks who or what created each record (`zoho.loginuser` for human actions, `zoho.adminuser` for automated tasks).

---

## Forms

### 1. regional_config

| Field Name | Type | Notes |
|-----------|------|-------|
| Merchant_Account | Single Line | Primary lookup key |
| Region | Single Line | UK, EU, BR, CH, JP, US, CA, AU, IN, MX, CO |
| Default_Currency | Single Line | ISO code (GBP, EUR, USD, etc.) |
| Default_LM_Name | Single Line | Lifestyle manager name |
| Default_LM_Email | Email | LM notification address |

### 2. dispute_reason_codes

| Field Name | Type | Notes |
|-----------|------|-------|
| Scheme | Single Line | visa, mc, amex |
| Code | Single Line | Reason code (e.g. 10.4, 4837, C02) |
| Description | Single Line | Human-readable reason |
| Category | Single Line | Fraud, Consumer Dispute, Processing Error |

### 3. chargeback_incidents

| Field Name | Type | Notes |
|-----------|------|-------|
| PSP_Reference | Single Line | Merchant platform reference ID |
| Platform | Drop Down | Adyen, Ingenico, Stripe |
| Merchant_Account | Single Line | Links to regional_config |
| Incident_Date | Date | Date of the chargeback event |
| Dispute_Deadline | Date | Auto-calculated: Incident_Date + 30 days |
| Days_Remaining | Number | Auto-calculated: days until deadline |
| Status | Drop Down | Open, Under Review, Disputed, Resolved, Expired, Won, Lost |
| Record_Type | Single Line | Chargeback, Second Chargeback, Fraud Alert, etc. |
| Currency_Original | Single Line | Original currency code |
| Amount_Original | Decimal | Original currency amount |
| Amount_USD | Decimal | Converted USD amount |
| Exchange_Rate | Decimal | Rate used for conversion |
| Dispute_Reason | Single Line | Reason code from merchant |
| Assigned_LM | Single Line | Auto-assigned from regional_config |

### 4. dispute_submissions

| Field Name | Type | Notes |
|-----------|------|-------|
| Incident_ID | Number | Links to chargeback_incidents.ID |
| Submission_Date | Date | Date dispute was submitted |
| Submitted_By | Single Line | Who submitted the dispute |
| Dispute_Reason_Text | Multi Line | Detailed reason for disputing |
| Evidence_Summary | Multi Line | Summary of evidence provided |
| Expected_Response_Date | Date | Auto-set: submission + 45 days |

### 5. audit_trail

| Field Name | Type | Notes |
|-----------|------|-------|
| Incident_ID | Number | Links to chargeback_incidents.ID |
| Action | Single Line | What happened |
| Action_Date | Date-Time | When it happened |
| Performed_By | Single Line | Who or SYSTEM |
| Notes | Multi Line | Detail text |

### 6. file_uploads

| Field Name | Type | Notes |
|-----------|------|-------|
| File_Name | Single Line | Uploaded file name |
| Platform | Single Line | Adyen, Ingenico, or Stripe |
| Incident_ID | Number | Linked chargeback if applicable |
| Processing_Status | Drop Down | Pending, Processing, Completed |
| Records_Found | Number | Records detected in file |
| Records_Imported | Number | Records successfully imported |

---

## Workflow Scripts

All scripts are in [`src/deluge/`](../). Each script includes a header comment with its exact location, trigger, and purpose. Paste each script into the corresponding Zoho Creator workflow location.

### Form Workflows

#### `chargeback_incident.on_success.dg`

**Location:** chargeback_incidents form > Workflow > On Success
**Trigger:** After successful form submission
**Source:** [`form-workflows/chargeback_incident.on_success.dg`](../form-workflows/chargeback_incident.on_success.dg)

**What it does:**

1. Looks up `regional_config` by Merchant_Account to find the assigned Lifestyle Manager and default currency
2. Sets `Assigned_LM` to the matched LM name
3. Calculates `Dispute_Deadline` as Incident_Date + 30 days
4. Calculates `Days_Remaining` as days between today and the deadline
5. Sets initial `Status` to "Open"
6. Defaults `Currency_Original` from regional config if blank
7. Creates an audit trail record with action "Chargeback Created", recording platform, amount, assigned LM, and deadline
8. Sends email notification to the assigned LM with chargeback details and deadline

**Notifications sent to:** Assigned Lifestyle Manager (via `Default_LM_Email` from regional_config)

---

#### `dispute_submission.on_success.dg`

**Location:** dispute_submissions form > Workflow > On Success
**Trigger:** After successful dispute submission
**Source:** [`form-workflows/dispute_submission.on_success.dg`](../form-workflows/dispute_submission.on_success.dg)

**What it does:**

1. Looks up the linked `chargeback_incidents` record by Incident_ID
2. Updates the chargeback status to "Disputed"
3. Sets `Expected_Response_Date` to submission date + 45 days (if not provided)
4. Creates an audit trail record with action "Dispute Submitted", recording the reason and evidence summary
5. Sends email notification to credit control with full dispute details

**Notifications sent to:** `creditcontrol@tengroup.com`

---

### Scheduled Tasks

#### `auto_alert_25_days.dg`

**Location:** Workflow > Schedules > Auto_Alert_25_Days
**Trigger:** Daily at 06:00
**Source:** [`scheduled/auto_alert_25_days.dg`](../scheduled/auto_alert_25_days.dg)

**What it does:**

1. Queries all chargebacks with status "Open" or "Under Review"
2. For each, calculates days since incident and updates `Days_Remaining`
3. **30+ days old:** Sets status to "Expired", creates audit trail entry ("Auto-Expired"), sends escalation email to credit control and the assigned LM
4. **25-29 days old:** Creates audit trail entry ("Deadline Warning Sent"), sends urgent warning to the assigned LM. If 3 or fewer days remain, also sends a critical alert to credit control

**Notifications sent to:** Assigned Lifestyle Manager, `creditcontrol@tengroup.com` (escalation and critical alerts)

---

#### `daily_file_processing.dg`

**Location:** Workflow > Schedules > Daily_File_Processing
**Trigger:** Daily at 02:00
**Source:** [`scheduled/daily_file_processing.dg`](../scheduled/daily_file_processing.dg)

**What it does:**

1. Queries all `file_uploads` with `Processing_Status` = "Pending"
2. Updates status to "Processing", creates audit trail entry
3. Validates file metadata (records found count)
4. Marks as "Completed", sets `Records_Imported` count, creates audit trail entry
5. Sends summary email to credit control with total files processed

**Notifications sent to:** `creditcontrol@tengroup.com`

---

#### `currency_conversion_batch.dg`

**Location:** Workflow > Schedules > Currency_Conversion_Batch
**Trigger:** Daily at 03:00
**Source:** [`scheduled/currency_conversion_batch.dg`](../scheduled/currency_conversion_batch.dg)

**What it does:**

1. Queries chargebacks where `Amount_USD` is null or 0
2. Fetches live exchange rates from the [Open Exchange Rates API](https://open.er-api.com/v6/latest/USD) (USD base)
3. For each unconverted record, divides `Amount_Original` by the currency rate to get USD
4. Sets `Amount_USD` and `Exchange_Rate` on the record
5. Creates audit trail entries for each conversion
6. Records needing manual review (missing or unsupported currency) are flagged in the audit trail

**External dependency:** `https://open.er-api.com/v6/latest/USD` (free tier, no API key required)

---

#### `data_cleansing_scheduled.dg`

**Location:** Workflow > Schedules > Data_Cleansing_Scheduled
**Trigger:** Daily at 04:00
**Source:** [`scheduled/data_cleansing_scheduled.dg`](../scheduled/data_cleansing_scheduled.dg)

**What it does:**

1. Queries chargebacks from the last 7 days
2. Normalizes `Record_Type` values by mapping common variations to standard values (e.g. "CB" → "Chargeback", "RFI" → "Request for Information", "NOC" → "Notification of Chargeback")
3. Validates `Currency_Original` against a list of known ISO currency codes
4. Validates `Amount_Original` is positive
5. Validates `Incident_Date` is not in the future
6. Validates `Platform` is one of the known platforms (Adyen, Ingenico, Stripe)
7. Creates audit trail entries for each cleansed or flagged record
8. Sends summary email to credit control with cleansed and flagged counts

**Notifications sent to:** `creditcontrol@tengroup.com`

---

### Custom APIs

#### `get_dashboard_summary.dg`

**Location:** Custom API > get_dashboard_summary
**Trigger:** GET request
**Source:** [`custom-api/get_dashboard_summary.dg`](../custom-api/get_dashboard_summary.dg)

**What it returns:**

```json
{
  "total_count": 324,
  "total_amount_usd": 303247.67,
  "active_risk_count": 42,
  "active_risk_amount_usd": 87500.00,
  "status_breakdown": {
    "Open": { "count": 30, "amount_usd": 65000.00 },
    "Under Review": { "count": 12, "amount_usd": 22500.00 },
    "...": "..."
  },
  "platform_breakdown": {
    "Adyen": { "count": 200, "amount_usd": 180000.00 },
    "...": "..."
  },
  "generated_at": "2026-04-14 10:30:00"
}
```

Active risk is defined as Open + Under Review (chargebacks not yet disputed).

**Access:** Credit Controller, CFO / COO

---

#### `get_aging_report.dg`

**Location:** Custom API > get_aging_report
**Trigger:** GET request
**Source:** [`custom-api/get_aging_report.dg`](../custom-api/get_aging_report.dg)

**What it returns:**

Aging buckets for active chargebacks (Open, Under Review, Disputed):

| Bucket | Significance |
|--------|-------------|
| 0-7 days | New, low urgency |
| 8-14 days | Active investigation window |
| 15-21 days | Evidence gathering should be underway |
| 22-25 days | Approaching deadline, warning threshold |
| 26-30 days | Critical, automated alerts active |
| 30+ days | Past deadline, should be expired |

The response includes `critical_count` and `critical_amount_usd` (22+ days), highlighting chargebacks at risk of missing the dispute window.

**Access:** Credit Controller, CFO / COO

---

### Setup

#### `install_app.dg`

**Location:** Microservices > Custom Functions > Install_App
**Trigger:** Run once after creating all 6 forms
**Source:** [`setup/install_app.dg`](install_app.dg)

**What it does:**

1. Seeds `regional_config` with 38 merchant account mappings across 10 countries
2. Seeds `dispute_reason_codes` with 13 reason codes (Visa, Mastercard, Amex)
3. Creates an initial audit trail entry recording the install

**After running `install_app.dg`:**

1. Update `regional_config` records with Lifestyle Manager names and email addresses
2. Paste the 2 form workflow scripts into their respective form On Success triggers
3. Create 4 scheduled tasks and paste the corresponding scripts
4. Create 2 custom API functions and paste the corresponding scripts
5. Import chargeback data via the ETL pipeline
