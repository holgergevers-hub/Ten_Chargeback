# Zoho Creator Form Schema

Create these 6 forms **in this order** before running `install_app.dg`.

## 1. regional_config

| Field Name | Type | Notes |
|-----------|------|-------|
| Merchant_Account | Single Line | Primary lookup key |
| Region | Single Line | UK, EU, BR, CH, JP, US, CA, AU, IN, MX, CO |
| Default_Currency | Single Line | ISO code (GBP, EUR, USD, etc.) |
| Default_LM_Name | Single Line | Lifestyle manager name |
| Default_LM_Email | Email | LM notification address |

## 2. dispute_reason_codes

| Field Name | Type | Notes |
|-----------|------|-------|
| Scheme | Single Line | visa, mc, amex |
| Code | Single Line | Reason code (e.g. 10.4, 4837, C02) |
| Description | Single Line | Human-readable reason |
| Category | Single Line | Fraud, Consumer Dispute, Processing Error |

## 3. chargeback_incidents

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

## 4. dispute_submissions

| Field Name | Type | Notes |
|-----------|------|-------|
| Incident_ID | Number | Links to chargeback_incidents.ID |
| Submission_Date | Date | Date dispute was submitted |
| Submitted_By | Single Line | Who submitted the dispute |
| Dispute_Reason_Text | Multi Line | Detailed reason for disputing |
| Evidence_Summary | Multi Line | Summary of evidence provided |
| Expected_Response_Date | Date | Auto-set: submission + 45 days |

## 5. audit_trail

| Field Name | Type | Notes |
|-----------|------|-------|
| Incident_ID | Number | Links to chargeback_incidents.ID |
| Action | Single Line | What happened |
| Action_Date | Date-Time | When it happened |
| Performed_By | Single Line | Who or SYSTEM |
| Notes | Multi Line | Detail text |

## 6. file_uploads

| Field Name | Type | Notes |
|-----------|------|-------|
| File_Name | Single Line | Uploaded file name |
| Platform | Single Line | Adyen, Ingenico, or Stripe |
| Incident_ID | Number | Linked chargeback if applicable |
| Processing_Status | Drop Down | Pending, Processing, Completed |
| Records_Found | Number | Records detected in file |
| Records_Imported | Number | Records successfully imported |
