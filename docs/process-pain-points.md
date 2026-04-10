# Pain Point Analysis

## Ten Group --- Chargeback Management

**Document Owner:** Finance Operations
**Last Updated:** April 2026
**Status:** Pain Point Assessment

---

## 1. Executive Summary

The current chargeback management process suffers from systemic issues that expose Ten Group to avoidable financial losses, compliance gaps, and operational inefficiency. This analysis identifies **10 distinct pain points**, categorized by severity. Three are rated Critical --- meaning they directly cause lost revenue or create unacceptable business risk.

### Severity Summary

| Severity | Count | Definition |
|---|---|---|
| **Critical** | 3 | Direct financial loss or regulatory/compliance exposure |
| **High** | 4 | Significant operational inefficiency or material risk of loss |
| **Medium** | 3 | Process friction that reduces effectiveness or scalability |

---

## 2. Pain Point Register

---

### PP-01: Manual Chargeback Identification

**Severity: CRITICAL**

**Description**
Credit controllers must manually log into three separate merchant platforms (Adyen, Ingenico, Stripe) and check up to 13 merchant accounts on each platform to identify new chargebacks. This amounts to up to 39 individual checks per scan cycle, with no defined frequency or schedule.

**Business Impact**
- Chargebacks may go undiscovered for days or weeks.
- The 30-day dispute window begins at chargeback issuance, not discovery. Every day of delay reduces the time available to investigate and respond.
- Chargebacks discovered after the 30-day window are automatically lost with no possibility of recovery.

**Risk**
Revenue leakage from expired dispute windows. The exact magnitude is unknown because there is no tracking of missed chargebacks.

---

### PP-02: No Automated Alerting or Deadline Tracking

**Severity: CRITICAL**

**Description**
There is no system that alerts the credit controller when a new chargeback is issued, when a dispute deadline is approaching, or when a deadline has passed. The 30-day window is tracked --- if at all --- through manual calendar entries or individual memory.

**Business Impact**
- No early warning when deadlines approach.
- No escalation when a chargeback is at risk of expiring without action.
- The CFO/COO has no visibility into how many chargebacks are within their dispute window versus how many are about to expire.

**Risk**
Silent financial loss. Chargebacks expire without anyone being aware they existed or that the deadline passed.

---

### PP-03: No Centralized Tracking or Audit Trail

**Severity: CRITICAL**

**Description**
Chargeback records exist across three merchant platforms, individual spreadsheets, and email threads. There is no single source of truth for the status of any given chargeback. There is no audit trail showing when a chargeback was identified, who was assigned to investigate it, what evidence was gathered, or what the outcome was.

**Business Impact**
- Impossible to report on chargeback volumes, win/loss rates, or financial exposure with confidence.
- No accountability --- if a chargeback is missed, there is no record to review.
- Audit and compliance teams cannot verify that chargebacks were handled within policy.
- Duplicate work may occur when multiple controllers encounter the same chargeback.

**Risk**
Compliance exposure, inability to demonstrate due diligence, and unquantifiable financial leakage.

---

### PP-04: Data Fragmentation Across Platforms

**Severity: HIGH**

**Description**
Chargeback data is spread across three platforms, each with a different data format:
- **Adyen**: CSV
- **Ingenico**: Pipe-delimited text
- **Stripe**: JSON

There is no common schema, no shared identifiers, and no automated aggregation. Consolidating data for reporting requires manual extraction and reformatting.

**Business Impact**
- Reporting requires hours of manual data manipulation.
- Errors are introduced during manual format conversion.
- Cross-platform analysis (e.g., "total chargeback exposure across all platforms") is not reliably available.

**Risk**
Inaccurate financial reporting and inability to assess total exposure.

---

### PP-05: Data Quality Issues

**Severity: HIGH**

**Description**
Of the 9,438 data files across all three platforms, the vast majority are empty or contain headers only. Meaningful data distribution is highly uneven:
- **Stripe**: Consistent data across all 13 merchant accounts.
- **Adyen**: Data present for only 1 of 13 merchant accounts.
- **Ingenico**: Data present for only 1 of 13 merchant accounts.

This means 24 of the 39 merchant accounts (across Adyen and Ingenico) either have no chargeback activity, are not configured to export data, or have a data pipeline failure that has gone undetected.

**Business Impact**
- Unknown whether missing data represents genuinely zero chargebacks or a data collection failure.
- If data is missing due to configuration issues, chargebacks on those accounts are completely invisible.
- Any analysis built on this data may dramatically understate actual exposure.

**Risk**
Material underreporting of chargeback volume and financial exposure. Potential undiscovered chargebacks across 24 merchant accounts.

---

### PP-06: No Structured Follow-Up Process

**Severity: HIGH**

**Description**
When a credit controller needs information from a Lifestyle Manager, they send an ad-hoc email. There is no standardized request template, no defined SLA for response, no automated reminder, and no escalation path. If the Lifestyle Manager does not respond, the controller must manually follow up --- repeatedly --- or abandon the investigation.

**Business Impact**
- Investigation timelines are unpredictable and often extend beyond the dispute window.
- Lifestyle Managers may not understand the urgency or the financial consequence of delayed responses.
- Evidence packages are inconsistent in quality and completeness.

**Risk**
Lost disputes due to insufficient evidence or expired deadlines caused by delayed internal communication.

---

### PP-07: Multi-Currency Complexity

**Severity: HIGH**

**Description**
Ten Group operates across 10 countries with transactions in multiple currencies. Chargeback amounts must be converted to a common reporting currency (USD) for consolidated financial reporting. This conversion is currently performed manually, with no standardized exchange rate source or conversion date methodology.

**Business Impact**
- Reported exposure figures may be inaccurate due to inconsistent conversion rates.
- Time-consuming manual calculation for each chargeback.
- No ability to automatically track currency exposure by region or trend over time.

**Risk**
Misstatement of financial exposure in management and board reporting.

---

### PP-08: No Executive Visibility

**Severity: MEDIUM**

**Description**
The CFO and COO have no real-time or near-real-time view of chargeback status, exposure, or trends. Any reporting they receive is manually compiled, typically lagging by days or weeks, and cannot be verified against source data.

**Business Impact**
- Strategic decisions about payment platform relationships, member risk, and dispute investment are made without current data.
- High-value chargebacks may not be escalated to leadership in time to influence the dispute outcome.
- Board and investor reporting on payment risk lacks rigor and timeliness.

**Risk**
Uninformed decision-making at the executive level. Inability to proactively manage payment risk.

---

### PP-09: Platform-Specific Dispute Processes

**Severity: MEDIUM**

**Description**
Each payment platform (Adyen, Ingenico, Stripe) has its own dispute submission interface, evidence requirements, and status tracking. The credit controller must remember which platform a chargeback originated from, navigate to the correct account, and follow that platform's specific process.

**Business Impact**
- Training burden increases with each platform.
- Higher error rate due to context-switching between different interfaces.
- Institutional knowledge is concentrated in individual controllers, creating key-person risk.

**Risk**
Process failures when staff change. Incorrect dispute submissions due to platform confusion.

---

### PP-10: No Scalability

**Severity: MEDIUM**

**Description**
The current process is entirely dependent on individual effort and manual steps. As Ten Group grows --- adding new markets, new merchant accounts, or new payment platforms --- the process does not scale. Each new account adds another manual check to the identification cycle.

**Business Impact**
- Headcount must increase linearly with chargeback volume.
- New market launches create immediate risk of unmonitored chargebacks until processes catch up.
- No ability to absorb volume spikes (e.g., seasonal increases, fraud events).

**Risk**
Process collapse under growth. Increasing proportion of chargebacks missed as volume grows.

---

## 3. Pain Point Impact Matrix

```
                    IMPACT ON REVENUE
                    Low         Medium        High
                +------------+------------+------------+
         High   |            |  PP-08     |  PP-01     |
                |            |  PP-09     |  PP-02     |
  LIKELIHOOD    |            |            |  PP-03     |
  OF            +------------+------------+------------+
  OCCURRENCE    |            |  PP-10     |  PP-04     |
         Medium |            |            |  PP-05     |
                |            |            |  PP-06     |
                +------------+------------+------------+
         Low    |            |            |  PP-07     |
                |            |            |            |
                +------------+------------+------------+
```

---

## 4. Cost of Inaction

Without intervention, the following outcomes are expected:

1. **Continued revenue leakage** from expired dispute windows, with no ability to quantify the loss.
2. **Increasing risk exposure** as transaction volumes grow with business expansion.
3. **Audit findings** when external or internal auditors examine the lack of controls around chargeback management.
4. **Key-person dependency** --- if the current credit controller leaves, institutional knowledge of the process is lost entirely.
5. **Inability to negotiate** with payment platforms, as there is no data to support conversations about chargeback rates, dispute success, or platform performance.

---

## 5. Document Control

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0 | April 2026 | Finance Operations | Initial pain point analysis |
