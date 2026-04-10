# Current State Process Map

## Ten Group --- Chargeback Management

**Document Owner:** Finance Operations
**Last Updated:** April 2026
**Status:** As-Is Process Documentation

---

## 1. Executive Summary

Ten Group's chargeback management process is entirely manual. Credit controllers must individually log into three separate merchant payment platforms --- Adyen, Ingenico, and Stripe --- across 13 merchant accounts spanning 10 countries. There is no centralized system, no automated alerting, and no unified tracking. The process relies on individual knowledge, ad-hoc communication, and manual spreadsheet reconciliation.

The company faces a hard constraint: **chargebacks must be disputed within 30 calendar days** of issuance or the funds are permanently lost.

---

## 2. Roles and Responsibilities

| Role | Responsibility | Current Tools |
|---|---|---|
| **Credit Controller** | Identify chargebacks, initiate investigations, compile evidence, submit disputes | Adyen portal, Ingenico portal, Stripe dashboard, email, spreadsheets |
| **Lifestyle Manager** | Provide transaction context and supporting evidence for disputed chargebacks | Email, internal CRM |
| **CFO / COO** | Oversee chargeback exposure, approve high-value disputes, monitor financial risk | Ad-hoc email reports, manual summaries |

---

## 3. Geographic Scope

Chargebacks are processed across **10 countries**, each with distinct merchant accounts and currency considerations:

| Region | Countries |
|---|---|
| Americas | United States, Brazil, Canada, Colombia, Mexico |
| EMEA | United Kingdom, European Union |
| Asia-Pacific | Japan, Australia, India |

Each country may transact in its local currency, requiring manual currency conversion for consolidated reporting.

---

## 4. Payment Platform Landscape

| Platform | Merchant Accounts | Data Format | Data Availability |
|---|---|---|---|
| **Stripe** | 13 | JSON | Consistent data across all 13 accounts |
| **Adyen** | 13 | CSV | Data present for 1 of 13 accounts only |
| **Ingenico** | 13 | Pipe-delimited | Data present for 1 of 13 accounts only |

**Total data files across all platforms:** 9,438 files. The majority are empty or contain headers only.

---

## 5. End-to-End Process Flow

### 5.1 Text-Based Process Diagram

```
                         CHARGEBACK IDENTIFICATION
                         -------------------------
    +------------------+     +------------------+     +------------------+
    |   Log into       |     |   Log into       |     |   Log into       |
    |   Adyen Portal   |     |   Ingenico       |     |   Stripe         |
    |   (13 accounts)  |     |   Portal         |     |   Dashboard      |
    |                  |     |   (13 accounts)  |     |   (13 accounts)  |
    +--------+---------+     +--------+---------+     +--------+---------+
             |                        |                        |
             v                        v                        v
    +------------------+     +------------------+     +------------------+
    |  Manually scan   |     |  Manually scan   |     |  Manually scan   |
    |  for new         |     |  for new         |     |  for new         |
    |  chargebacks     |     |  chargebacks     |     |  chargebacks     |
    +--------+---------+     +--------+---------+     +--------+---------+
             |                        |                        |
             +------------+-----------+                        |
                          |                                    |
                          +------------------------------------+
                          |
                          v
               +---------------------+
               |  Record chargeback  |
               |  details in         |    <-- Manual entry into spreadsheet
               |  spreadsheet        |        (amount, date, merchant, reason)
               +----------+----------+
                          |
                          |   *** 30-DAY DISPUTE WINDOW STARTS ***
                          |
                          v
               +---------------------+
               |  REVIEW &           |
               |  INVESTIGATION      |
               +----------+----------+
                          |
                          v
               +---------------------+
               |  Identify the       |
               |  Lifestyle Manager  |    <-- Credit Controller must determine
               |  who handled the    |        which LM handled the original
               |  original           |        member transaction
               |  transaction        |
               +----------+----------+
                          |
                          v
               +---------------------+
               |  Email Lifestyle    |
               |  Manager requesting |    <-- No template, no tracking,
               |  transaction        |        no escalation if no response
               |  context &          |
               |  evidence           |
               +----------+----------+
                          |
                          v
               +---------------------+
               |  WAIT FOR           |
               |  RESPONSE           |    <-- Unpredictable turnaround
               |                     |        No automated follow-up
               |  (days to weeks)    |
               +----------+----------+
                          |
                  +-------+--------+
                  |                 |
                  v                 v
         +-------------+   +---------------+
         |  Response   |   |  No Response  |
         |  received   |   |  / Incomplete |
         +------+------+   +-------+-------+
                |                   |
                v                   v
         +-------------+   +---------------+
         |  Compile    |   |  Manual       |
         |  evidence   |   |  follow-up    |
         |  package    |   |  (email/call) |    <-- Repeat until response
         +------+------+   +-------+-------+        or deadline passes
                |                   |
                +-------+-----------+
                        |
                        v
               +---------------------+
               |  DISPUTE            |
               |  SUBMISSION         |
               +----------+----------+
                          |
                          v
               +---------------------+
               |  Log back into      |
               |  original merchant  |    <-- Must remember which platform
               |  platform           |        and which merchant account
               +----------+----------+
                          |
                          v
               +---------------------+
               |  Submit dispute     |
               |  with evidence via  |    <-- Each platform has different
               |  platform-specific  |        submission requirements
               |  process            |        and interfaces
               +----------+----------+
                          |
                          v
               +---------------------+
               |  TRACKING &         |
               |  OUTCOME            |
               +----------+----------+
                          |
                          v
               +---------------------+
               |  Manually check     |
               |  platform for       |    <-- No notification when
               |  dispute outcome    |        outcome is determined
               +----------+----------+
                          |
                  +-------+--------+
                  |                 |
                  v                 v
         +-------------+   +---------------+
         |  Won        |   |  Lost         |
         |  (funds     |   |  (funds       |
         |  recovered) |   |  written off) |
         +------+------+   +-------+-------+
                |                   |
                +-------+-----------+
                        |
                        v
               +---------------------+
               |  Update spreadsheet |    <-- Manual, error-prone
               |  with outcome       |        Often delayed or missed
               +---------------------+
```

### 5.2 Process Steps Detail

#### Step 1: Chargeback Identification

The Credit Controller logs into each of the three merchant platforms individually. For each platform, they must check up to 13 separate merchant accounts. This means up to **39 individual login-and-check cycles** to perform a complete scan. There is no defined frequency for this check --- it depends on the controller's workload and memory.

#### Step 2: Recording

When a chargeback is found, the controller manually records it in a spreadsheet. Fields captured vary by controller and are not standardized. There is no unique identifier linking the spreadsheet entry back to the source platform record.

#### Step 3: Investigation Assignment

The controller must determine which Lifestyle Manager handled the original member transaction. This often requires cross-referencing internal systems and relies on institutional knowledge. There is no automated lookup.

#### Step 4: Evidence Gathering

The controller emails the Lifestyle Manager requesting context and evidence. There is no standardized request template, no SLA for response time, and no automated escalation. Responses may take days or weeks. Some requests receive no response at all.

#### Step 5: Dispute Submission

The controller returns to the original merchant platform and submits the dispute through that platform's specific interface. Each platform has different requirements for evidence format and submission process.

#### Step 6: Outcome Tracking

The controller must periodically log back into the platform to check whether a dispute has been resolved. There is no push notification or automated status update. Outcomes may go unrecorded for weeks.

---

## 6. Critical Constraints

| Constraint | Detail |
|---|---|
| **30-day dispute window** | Chargebacks not disputed within 30 calendar days are automatically lost. This clock starts when the chargeback is issued by the card network, not when the controller discovers it. |
| **Multi-currency** | Transactions span 10+ currencies. There is no automated conversion to a base reporting currency. |
| **Three platforms, three formats** | Each platform exports data differently (CSV, JSON, pipe-delimited), making consolidation manual and error-prone. |
| **39 merchant accounts** | 13 accounts per platform requires repetitive, time-consuming manual checks. |

---

## 7. Process Frequency and Volume

The current process has no defined cadence. Credit controllers check platforms when they can, creating an inherent risk that chargebacks are discovered late --- or not at all --- within the 30-day window.

There is no historical baseline for chargeback volume because tracking has been inconsistent. Establishing this baseline is a prerequisite for any process improvement initiative.

---

## 8. Document Control

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0 | April 2026 | Finance Operations | Initial current-state documentation |
