# Future State Process Model

## Ten Group --- Chargeback Management

**Document Owner:** Finance Operations
**Last Updated:** April 2026
**Status:** Target Operating Model

---

## 1. Executive Summary

The future-state chargeback management system replaces Ten Group's manual, fragmented process with a centralized, automated platform built on **Zoho Creator**. The system will automatically ingest chargeback data from all three merchant platforms (Adyen, Ingenico, Stripe), normalize it into a unified format, provide proactive alerting against the 30-day dispute window, and deliver real-time visibility to both operations staff and executive leadership.

The goal is simple: **no chargeback should ever expire without a conscious decision not to dispute it.**

---

## 2. Design Principles

| Principle | Application |
|---|---|
| **Automate identification** | The system discovers chargebacks; people do not hunt for them |
| **Enforce deadlines** | The 30-day window is tracked automatically with escalating alerts |
| **Centralize everything** | One system, one view, one audit trail --- regardless of source platform |
| **Surface risk to leadership** | CFO/COO see exposure in real time, not in retrospective spreadsheets |
| **Scale without headcount** | Adding a new merchant, country, or platform requires configuration, not additional staff |

---

## 3. Future State Process Flow

### 3.1 Text-Based Process Diagram

```
    +=====================================================================+
    |                     AUTOMATED DATA INGESTION                         |
    +=====================================================================+
    |                                                                       |
    |   +-----------+      +-------------+      +-----------+              |
    |   |  Adyen    |      |  Ingenico   |      |  Stripe   |              |
    |   |  (CSV)    |      |  (Pipe-     |      |  (JSON)   |              |
    |   |           |      |  delimited) |      |           |              |
    |   +-----+-----+      +------+------+      +-----+-----+              |
    |         |                    |                    |                    |
    |         v                    v                    v                    |
    |   +-----------------------------------------------------------+      |
    |   |           ETL Pipeline (Python, stdlib only)              |      |
    |   |                                                           |      |
    |   |  - Extract from ZIP/files                                 |      |
    |   |  - Parse CSV, pipe-delimited, JSON                        |      |
    |   |  - Skip empty/header-only files                           |      |
    |   |  - Normalize to unified schema                            |      |
    |   |  - Convert all amounts to USD                             |      |
    |   |  - Deduplicate across platforms                           |      |
    |   |  - Flag data quality issues                               |      |
    |   +----------------------------+------------------------------+      |
    |                                |                                      |
    +================================|======================================+
                                     |
                                     v
    +=====================================================================+
    |                    ZOHO CREATOR PLATFORM                              |
    +=====================================================================+
    |                                                                       |
    |   +-----------------------------------------------------------+      |
    |   |              Chargeback Master Record                     |      |
    |   |                                                           |      |
    |   |  - Unique ID        - Original currency + USD amount     |      |
    |   |  - Source platform   - Dispute deadline (auto-calculated) |      |
    |   |  - Merchant account  - Status (New/Investigating/         |      |
    |   |  - Country/region      Disputed/Won/Lost/Expired)        |      |
    |   |  - Chargeback date   - Assigned controller               |      |
    |   |  - Reason code       - Full audit trail                  |      |
    |   +----------------------------+------------------------------+      |
    |                                |                                      |
    |                                v                                      |
    |   +-----------------------------------------------------------+      |
    |   |              SMART ALERTING ENGINE                        |      |
    |   +-----------------------------------------------------------+      |
    |   |                                                           |      |
    |   |  Day 0:  New chargeback alert --> Credit Controller      |      |
    |   |          Auto-assign based on merchant/region             |      |
    |   |                                                           |      |
    |   |  Day 5:  Status check --- is investigation started?       |      |
    |   |          If NO --> reminder to assigned controller        |      |
    |   |                                                           |      |
    |   |  Day 15: Midpoint check --- is evidence gathered?         |      |
    |   |          If NO --> escalate to controller + manager       |      |
    |   |                                                           |      |
    |   |  Day 25: CRITICAL DEADLINE WARNING                       |      |
    |   |          --> Controller, Manager, CFO/COO                |      |
    |   |          5 days remaining to dispute                      |      |
    |   |                                                           |      |
    |   |  Day 30: EXPIRED --- auto-mark as Expired if no dispute  |      |
    |   |          --> CFO/COO notification                        |      |
    |   +----------------------------+------------------------------+      |
    |                                |                                      |
    |                                v                                      |
    |   +-----------------------------------------------------------+      |
    |   |              INVESTIGATION WORKFLOW                       |      |
    |   +-----------------------------------------------------------+      |
    |                                |                                      |
    |         +----------------------+----------------------+               |
    |         |                      |                      |               |
    |         v                      v                      v               |
    |   +------------+      +--------------+      +---------------+        |
    |   | Auto-send  |      | Track LM     |      | Evidence      |        |
    |   | templated  |      | response     |      | package       |        |
    |   | request to |      | with auto-   |      | assembly &    |        |
    |   | Lifestyle  |      | escalation   |      | checklist     |        |
    |   | Manager    |      | on no-reply  |      |               |        |
    |   +------------+      +--------------+      +---------------+        |
    |                                                                       |
    |                                v                                      |
    |   +-----------------------------------------------------------+      |
    |   |              DISPUTE & OUTCOME TRACKING                  |      |
    |   +-----------------------------------------------------------+      |
    |   |                                                           |      |
    |   |  - Record dispute submission date and platform           |      |
    |   |  - Track outcome (Won / Lost) with amounts               |      |
    |   |  - Calculate recovery rate by platform, region, reason   |      |
    |   |  - Full audit trail of every action and status change    |      |
    |   +----------------------------+------------------------------+      |
    |                                |                                      |
    |                                v                                      |
    |   +-----------------------------------------------------------+      |
    |   |              CFO / COO DASHBOARD                         |      |
    |   +-----------------------------------------------------------+      |
    |   |                                                           |      |
    |   |  - Total open exposure (USD)                             |      |
    |   |  - Chargebacks by status, platform, region               |      |
    |   |  - Deadline risk view (approaching 30-day expiry)        |      |
    |   |  - Win/loss rate trends                                  |      |
    |   |  - Recovery amounts and rates                            |      |
    |   |  - Aging analysis                                        |      |
    |   +-----------------------------------------------------------+      |
    |                                                                       |
    +=====================================================================+
```

---

## 4. Pain Point Resolution Map

Every pain point identified in the current-state analysis is addressed by a specific capability in the future state.

| Ref | Pain Point | Severity | Future State Solution |
|---|---|---|---|
| PP-01 | Manual chargeback identification | Critical | **Automated ingestion** --- ETL pipeline processes all files from all platforms on a scheduled basis. New chargebacks are surfaced automatically. |
| PP-02 | No alerting or deadline tracking | Critical | **Smart alerting engine** --- Automated notifications at Day 0, 5, 15, 25, and 30. Escalation to CFO/COO at Day 25. Auto-expiry at Day 30. |
| PP-03 | No centralized tracking or audit trail | Critical | **Zoho Creator master record** --- Single source of truth with full audit trail. Every status change, assignment, and action is logged with timestamp and user. |
| PP-04 | Data fragmentation across platforms | High | **ETL normalization** --- Python pipeline parses CSV, JSON, and pipe-delimited files into a unified schema before loading into Zoho Creator. |
| PP-05 | Data quality issues | High | **Quality flagging** --- Pipeline skips empty/header-only files, logs data quality issues, and alerts when expected data is missing from merchant accounts. |
| PP-06 | No structured follow-up process | High | **Templated requests with auto-escalation** --- Standardized email templates sent automatically. Non-response triggers escalation after defined intervals. |
| PP-07 | Multi-currency complexity | High | **Automatic USD conversion** --- All amounts converted to USD at ingestion using standardized exchange rates. Original currency preserved for reference. |
| PP-08 | No executive visibility | Medium | **Real-time dashboard** --- CFO/COO dashboard with live exposure, deadline risk, and trend views. Built with HTML/JS and Chart.js. |
| PP-09 | Platform-specific dispute processes | Medium | **Centralized workflow** --- All investigation and evidence gathering managed in one system, regardless of originating platform. Platform-specific submission instructions embedded in workflow. |
| PP-10 | No scalability | Medium | **Configuration-driven growth** --- New merchants, countries, or platforms added via configuration. No process redesign required. |

---

## 5. Current State vs. Future State Comparison

| Dimension | Current State | Future State |
|---|---|---|
| **Chargeback discovery** | Manual login to 3 platforms, 39 accounts | Automated ingestion and alerting |
| **Time to identify** | Days to weeks (or never) | Same day as data is available |
| **Deadline tracking** | Individual memory / calendar | Automated alerts at Day 0, 5, 15, 25, 30 |
| **Escalation** | None | Auto-escalation at Day 15 and Day 25 |
| **Data format** | 3 formats (CSV, JSON, pipe-delimited) | Unified normalized schema |
| **Currency handling** | Manual, inconsistent | Automatic USD conversion at ingestion |
| **Investigation workflow** | Ad-hoc email | Templated requests with SLA tracking |
| **Audit trail** | None | Full trail --- every action logged |
| **Executive reporting** | Manual spreadsheet, lagging | Real-time dashboard |
| **Tracking system** | Individual spreadsheets | Centralized Zoho Creator records |
| **Scalability** | Linear headcount increase | Configuration-driven, no headcount dependency |
| **Data quality monitoring** | None | Automated quality checks and missing-data alerts |
| **Recovery visibility** | Unknown | Win/loss rates by platform, region, reason code |
| **Risk of missed chargebacks** | High and unquantifiable | Near zero with monitoring |

---

## 6. Zoho Creator Implementation Approach

### 6.1 Why Zoho Creator

Zoho Creator is selected as the platform because:
- Ten Group has an existing Zoho ecosystem, minimizing integration overhead.
- Creator provides low-code form and workflow capabilities suitable for the credit controller user base.
- Deluge scripting supports the automation logic required for alerting, assignment, and escalation.
- Built-in reporting can be supplemented with the custom HTML/JS dashboard for executive use.

### 6.2 Application Architecture

```
+------------------------------------------------------------------+
|                      Zoho Creator App                             |
+------------------------------------------------------------------+
|                                                                    |
|  FORMS                           WORKFLOWS (Deluge)               |
|  -----                           --------------------              |
|  - Chargeback Record             - On Create: auto-assign,        |
|  - Investigation Details           calculate deadline, send       |
|  - Evidence Attachments            Day 0 alert                    |
|  - Dispute Submission            - Scheduled: deadline checks      |
|  - Outcome Recording               (Day 5, 15, 25, 30)           |
|                                  - On Edit: audit trail logging    |
|  REPORTS                         - On Status Change: notifications |
|  -------                                                           |
|  - Open Chargebacks              CUSTOM APIs                      |
|  - Approaching Deadlines         -----------                       |
|  - Win/Loss Summary              - ETL data import endpoint       |
|  - Regional Exposure             - Dashboard data feed            |
|                                  - Email webhook receiver         |
|  VIEWS                                                             |
|  -----                           INTEGRATIONS                     |
|  - My Assigned Chargebacks       ------------                      |
|  - All Open (CFO view)           - Zoho Mail (notifications)      |
|  - Expired / At Risk             - Exchange rate service          |
|                                  - Custom dashboard (HTML/JS)     |
+------------------------------------------------------------------+
```

### 6.3 Data Model (Core Entities)

| Entity | Key Fields | Purpose |
|---|---|---|
| **Chargeback** | ID, source_platform, merchant_account, country, chargeback_date, dispute_deadline, original_amount, original_currency, usd_amount, reason_code, status, assigned_to | Master record for every chargeback |
| **Investigation** | chargeback_id, lifestyle_manager, request_date, response_date, evidence_summary, follow_up_count | Tracks the internal investigation |
| **Dispute** | chargeback_id, submission_date, platform_reference, evidence_files, outcome, outcome_date, recovered_amount | Records dispute submission and result |
| **Audit_Log** | chargeback_id, timestamp, user, action, old_value, new_value | Immutable log of every change |
| **Alert_History** | chargeback_id, alert_type, sent_date, recipients | Record of all automated notifications |

### 6.4 ETL Pipeline

The Python ETL pipeline handles all data transformation outside Zoho Creator:

1. **Extract** --- Unzip and read files from all three platforms.
2. **Parse** --- Handle CSV (Adyen), pipe-delimited (Ingenico), and JSON (Stripe) formats.
3. **Filter** --- Skip empty and header-only files (the majority of the 9,438 files).
4. **Normalize** --- Map platform-specific fields to the unified schema.
5. **Convert** --- Transform all amounts to USD using standardized exchange rates.
6. **Deduplicate** --- Identify and merge any cross-platform duplicates.
7. **Load** --- Push normalized records to Zoho Creator via custom API.

The pipeline uses Python standard library only (csv, json, zipfile, pathlib, datetime) with no external dependencies.

### 6.5 Alerting Schedule

| Trigger | Recipients | Channel | Message |
|---|---|---|---|
| **Day 0** --- New chargeback ingested | Assigned Credit Controller | Email | New chargeback requiring investigation. Details and deadline included. |
| **Day 5** --- Status still "New" | Assigned Credit Controller | Email | Reminder: investigation not started. 25 days remaining. |
| **Day 15** --- Status not "Disputed" | Credit Controller + their Manager | Email | Midpoint warning: evidence not yet gathered. 15 days remaining. |
| **Day 25** --- Status not "Disputed" | Credit Controller + Manager + CFO/COO | Email | **Critical**: 5 days remaining. Immediate action required. |
| **Day 30** --- No dispute submitted | CFO/COO | Email | Chargeback expired. Auto-marked as Expired. Post-mortem required. |

### 6.6 Dashboard Components

The CFO/COO dashboard (HTML/JS with Chart.js) provides:

| Component | Visualization | Purpose |
|---|---|---|
| **Exposure Summary** | KPI cards | Total open USD exposure, count by status |
| **Deadline Risk** | Color-coded table | Chargebacks ordered by days remaining, red/amber/green |
| **Platform Breakdown** | Bar chart | Chargeback volume and value by platform |
| **Regional View** | Bar chart by country | Exposure by operating country |
| **Trend Analysis** | Line chart | Monthly chargeback volume and recovery rate |
| **Win/Loss Rate** | Donut chart | Dispute outcomes with recovery amounts |

---

## 7. Implementation Phases

| Phase | Scope | Outcome |
|---|---|---|
| **Phase 1: Foundation** | ETL pipeline, Zoho Creator forms and master record, basic import | Chargebacks from all platforms visible in one system |
| **Phase 2: Automation** | Alerting engine, auto-assignment, deadline tracking, email templates | No chargeback expires without notification |
| **Phase 3: Workflow** | Investigation tracking, LM follow-up automation, evidence management | Structured investigation process with accountability |
| **Phase 4: Visibility** | CFO/COO dashboard, reporting views, trend analysis | Real-time executive visibility into chargeback risk |

---

## 8. Success Metrics

| Metric | Current Baseline | Target |
|---|---|---|
| Chargebacks identified within 48 hours | Unknown | 100% |
| Chargebacks expired without action | Unknown | 0% |
| Average time from identification to dispute | Unknown | < 15 days |
| Dispute win rate | Unknown | Tracked and improving quarter-over-quarter |
| Time to generate executive report | Hours (manual) | Real-time (dashboard) |
| Audit trail completeness | 0% | 100% |

---

## 9. Document Control

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0 | April 2026 | Finance Operations | Initial future-state documentation |
