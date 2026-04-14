"""
Merge the base .ds (from Zoho Creator / Zia) with the Ten Chargeback project
configuration to produce a complete deployable .ds file.

Operations performed:
  1. Upgrade chargeback_incidents: add 18 new fields + fix status picklist
  2. Insert 8 new forms (config, lookups, operational, audit)
  3. Add 6 new reports (keep base reports with conditional formatting)
  4. Wire in 2 Deluge form workflows
  5. Wire in 4 Deluge scheduled scripts
  6. Add web > reports entries for new reports
  7. Add web/phone/tablet form entries + menu sections

Preserves: blueprints, custom roles, rich dashboard, conditional formatting,
           kanban report, invoices form (38 fields).
"""

import argparse
import re
import sys
from pathlib import Path

parser = argparse.ArgumentParser(description="Merge base .ds with Ten Chargeback project config")
parser.add_argument("--no-scripts", action="store_true", help="Skip embedding Deluge scripts (for debugging)")
args = parser.parse_args()

INPUT = Path(r"c:\Users\User\Downloads\Chargeback_Management_System.ds")
OUTPUT = Path(r"c:\Users\User\OneDrive\Documents\GitHub\Ten_Chargeback\ten_chargeback_management.ds")
PROJECT_ROOT = Path(r"c:\Users\User\OneDrive\Documents\GitHub\Ten_Chargeback")

with open(INPUT, "r", encoding="utf-8") as f:
    lines = f.readlines()


# ── HELPERS ──────────────────────────────────────────────────

def field_block(name, ftype, display, extra=None):
    """Generate a single field block."""
    extra = extra or []
    b = []
    b.append(f"\t\t\t{name}")
    b.append(f"\t\t\t(")
    b.append(f"    \t\t\ttype = {ftype}")
    b.append(f'\t\t\t\tdisplayname = "{display}"')
    for e in extra:
        b.append(f"\t\t\t\t{e}")
    b.append(f"\t \t\t\trow = 1")
    b.append(f"\t \t\t\tcolumn = 1")
    b.append(f"\t\t\t\twidth = medium")
    b.append(f"\t\t\t)")
    return [l + "\n" for l in b]


def form_block(name, display, fields):
    """Generate a form block matching base .ds format."""
    b = []
    b.append(f"\t\tform {name}")
    b.append(f"\t\t{{")
    b.append(f'\t\t\tdisplayname = "{display}"')
    b.append(f'\t\t\tsuccess message = "{display} Added Successfully"')
    b.append(f"\t\t\tSection")
    b.append(f"\t\t\t(")
    b.append(f"\t\t\t\ttype = section")
    b.append(f"\t \t\t\trow = 1")
    b.append(f"\t \t\t\tcolumn = 0")
    b.append(f"\t\t\t\twidth = medium")
    b.append(f"\t\t\t)")
    for fname, ftype, fdisplay, extra in fields:
        b.append(f"\t\t\t{fname}")
        b.append(f"\t\t\t(")
        b.append(f"    \t\t\ttype = {ftype}")
        b.append(f'\t\t\t\tdisplayname = "{fdisplay}"')
        for e in extra:
            b.append(f"\t\t\t\t{e}")
        b.append(f"\t \t\t\trow = 1")
        b.append(f"\t \t\t\tcolumn = 1")
        b.append(f"\t\t\t\twidth = medium")
        b.append(f"\t\t\t)")
    b.append(f"")
    b.append(f"\t\t\tactions")
    b.append(f"\t\t\t{{")
    b.append(f"\t\t\t\ton add")
    b.append(f"\t\t\t\t{{")
    b.append(f"\t\t\t\t\tsubmit")
    b.append(f"\t\t\t\t\t(")
    b.append(f"   \t\t\t\t\t\ttype = submit")
    b.append(f'   \t\t\t\t\t\tdisplayname = "Submit"')
    b.append(f"\t\t\t\t\t)")
    b.append(f"\t\t\t\t\treset")
    b.append(f"\t\t\t\t\t(")
    b.append(f"   \t\t\t\t\t\ttype = reset")
    b.append(f'   \t\t\t\t\t\tdisplayname = "Reset"')
    b.append(f"\t\t\t\t\t)")
    b.append(f"\t\t\t\t}}")
    b.append(f"\t\t\t\ton edit")
    b.append(f"\t\t\t\t{{")
    b.append(f"\t\t\t\t\tupdate")
    b.append(f"\t\t\t\t\t(")
    b.append(f"   \t\t\t\t\t\ttype = submit")
    b.append(f'   \t\t\t\t\t\tdisplayname = "Update"')
    b.append(f"\t\t\t\t\t)")
    b.append(f"\t\t\t\t\tcancel")
    b.append(f"\t\t\t\t\t(")
    b.append(f"   \t\t\t\t\t\ttype = cancel")
    b.append(f'   \t\t\t\t\t\tdisplayname = "Cancel"')
    b.append(f"\t\t\t\t\t)")
    b.append(f"\t\t\t\t}}")
    b.append(f"\t\t\t}}")
    b.append(f"\t\t}}")
    return [l + "\n" for l in b]


def report_block(name, display, form, columns, filter_expr=""):
    """Generate a list report block."""
    b = []
    b.append(f"\t\tlist {name}")
    b.append(f"\t\t{{")
    b.append(f'\t\t\tdisplayName = "All {display}"')
    if filter_expr:
        b.append(f"\t\t\tshow all rows from {form}  [{filter_expr}]  ")
    else:
        b.append(f"\t\t\tshow all rows from {form}    ")
    b.append(f"\t\t\t(")
    for col in columns:
        b.append(f'\t\t\t\t{col} as "{col}"')
    b.append(f"\t\t\t)")
    b.append(f"\t\t}}")
    return [l + "\n" for l in b]


def web_report_block(report_name, columns):
    """Generate web > reports entry with quickview, detailview, and menu."""
    b = []
    b.append(f"\t\t\treport {report_name}")
    b.append(f"\t\t\t{{")
    # quickview
    b.append(f"\t\t\t\tquickview")
    b.append(f"\t\t\t\t(")
    b.append(f"\t\t\t\t\tlayout")
    b.append(f"\t\t\t\t\t(")
    b.append(f"\t\t\t\t\t\ttype = -1")
    b.append(f"\t\t\t\t\t\tdatablock1")
    b.append(f"\t\t\t\t\t\t(")
    b.append(f"\t\t\t\t\t\t\tlayout type = -1")
    b.append(f"\t\t\t\t\t\t\tfields")
    b.append(f"\t\t\t\t\t\t\t(")
    for c in columns:
        b.append(f"\t\t\t\t\t\t\t\t{c}")
    b.append(f"\t\t\t\t\t\t\t)")
    b.append(f"\t\t\t\t\t\t)")
    b.append(f"\t\t\t\t\t)")
    b.append(f"\t\t\t\t\tmenu")
    b.append(f"\t\t\t\t\t(")
    b.append(f"\t\t\t\t\t\theader")
    b.append(f"\t\t\t\t\t\t(")
    b.append(f"\t\t\t\t\t\t\tEdit ")
    b.append(f"\t\t\t\t\t\t\tDuplicate ")
    b.append(f"\t\t\t\t\t\t\tDelete ")
    b.append(f"\t\t\t\t\t\t\tPrint ")
    b.append(f"\t\t\t\t\t\t\tAdd ")
    b.append(f"\t\t\t\t\t\t\tImport ")
    b.append(f"\t\t\t\t\t\t\tExport ")
    b.append(f"\t\t\t\t\t\t)")
    b.append(f"\t\t\t\t\t\trecord")
    b.append(f"\t\t\t\t\t\t(")
    b.append(f"\t\t\t\t\t\t\tEdit   \t   ")
    b.append(f"\t\t\t\t\t\t\tDuplicate   \t   ")
    b.append(f"\t\t\t\t\t\t\tDelete   \t   ")
    b.append(f"\t\t\t\t\t\t\tPrint   \t   ")
    b.append(f"\t\t\t\t\t\t)")
    b.append(f"\t\t\t\t\t)")
    b.append(f"\t\t\t\t\taction")
    b.append(f"\t\t\t\t\t(")
    b.append(f"\t\t\t\t\t\ton click")
    b.append(f"\t\t\t\t\t\t(")
    b.append(f"\t\t\t\t\t\t\tView Record   \t   ")
    b.append(f"\t\t\t\t\t\t)")
    b.append(f"\t\t\t\t\t\ton right click")
    b.append(f"\t\t\t\t\t\t(")
    b.append(f"\t\t\t\t\t\t\tEdit   \t   ")
    b.append(f"\t\t\t\t\t\t\tDuplicate   \t   ")
    b.append(f"\t\t\t\t\t\t\tDelete   \t   ")
    b.append(f"\t\t\t\t\t\t\tPrint   \t   ")
    b.append(f"\t\t\t\t\t\t\tView Record   \t   ")
    b.append(f"\t\t\t\t\t\t)")
    b.append(f"\t\t\t\t\t)")
    b.append(f"\t\t\t\t)")
    b.append(f"")
    # detailview
    b.append(f"\t\t\t\tdetailview")
    b.append(f"\t\t\t\t(")
    b.append(f"\t\t\t\t\tlayout")
    b.append(f"\t\t\t\t\t(")
    b.append(f"\t\t\t\t\t\ttype = 1")
    b.append(f"\t\t\t\t\t\tdatablock1")
    b.append(f"\t\t\t\t\t\t(")
    b.append(f"\t\t\t\t\t\t\tlayout type = -2")
    b.append(f'\t\t\t\t\t\t\ttitle = "Overview"')
    b.append(f"\t\t\t\t\t\t\tfields")
    b.append(f"\t\t\t\t\t\t\t(")
    for c in columns:
        b.append(f"\t\t\t\t\t\t\t\t{c}")
    b.append(f"\t\t\t\t\t\t\t)")
    b.append(f"\t\t\t\t\t\t)")
    b.append(f"\t\t\t\t\t)")
    b.append(f"\t\t\t\t\tmenu")
    b.append(f"\t\t\t\t\t(")
    b.append(f"\t\t\t\t\t\theader")
    b.append(f"\t\t\t\t\t\t(")
    b.append(f"\t\t\t\t\t\t\tEdit ")
    b.append(f"\t\t\t\t\t\t\tDuplicate ")
    b.append(f"\t\t\t\t\t\t\tDelete ")
    b.append(f"\t\t\t\t\t\t\tPrint ")
    b.append(f"\t\t\t\t\t\t)")
    b.append(f"\t\t\t\t\t)")
    b.append(f"\t\t\t\t)")
    b.append(f"\t\t\t}}")
    return [l + "\n" for l in b]


def read_deluge_script(path):
    """Read a .dg file, strip header comments, return code lines."""
    text = path.read_text(encoding="utf-8")
    code_lines = []
    past_header = False
    for line in text.splitlines():
        stripped = line.strip()
        if not past_header:
            if stripped.startswith("//") or stripped == "":
                continue
            past_header = True
        code_lines.append(line)
    return "\n".join(code_lines)


def indent_code(code, tab_depth):
    """Re-indent Deluge code for embedding in .ds workflow blocks."""
    result = []
    for line in code.splitlines():
        if line.strip() == "":
            result.append("")
        else:
            result.append("\t" * tab_depth + line)
    return "\n".join(result)


def workflow_block(link_name, display_name, form, record_event, event_type, code):
    """Generate a form workflow block with embedded Deluge code."""
    b = []
    b.append(f'\t\t\t{link_name} as "{display_name}"')
    b.append(f"\t\t\t{{")
    b.append(f"\t\t\t\ttype =  form")
    b.append(f"\t\t\t\tform = {form}")
    b.append(f"")
    b.append(f"\t\t\t\trecord event = {record_event}")
    b.append(f"")
    b.append(f"\t\t\t\t{event_type}")
    b.append(f"\t\t\t\t{{")
    b.append(f"\t\t\t\t\tactions ")
    b.append(f"\t\t\t\t\t{{")
    b.append(f"\t\t\t\t\t\tcustom deluge script")
    b.append(f"\t\t\t\t\t\t(")
    b.append(indent_code(code, 7))
    b.append(f"\t\t\t\t\t\t)")
    b.append(f"\t\t\t\t\t}}")
    b.append(f"\t\t\t\t}}")
    b.append(f"")
    b.append(f"\t\t\t}}")
    return [l + "\n" for l in b]


def schedule_block(link_name, display_name, form, code):
    """Generate a scheduled task block with embedded Deluge code."""
    b = []
    b.append(f'\t\t\t{link_name} as "{display_name}"')
    b.append(f"\t\t\t{{")
    b.append(f"\t\t\t\ttype =  schedule")
    b.append(f"\t\t\t\tform = {form}")
    b.append(f'\t\t\t\ttime zone = "America/Los_Angeles"')
    b.append(f"\t\t\t\ton start")
    b.append(f"\t\t\t\t{{")
    b.append(f"\t\t\t\t\tactions ")
    b.append(f"\t\t\t\t\t{{")
    b.append(f"\t\t\t\t\ton load")
    b.append(f"\t\t\t\t\t(")
    b.append(indent_code(code, 6))
    b.append(f"\t\t\t\t\t)")
    b.append(f"\t\t\t\t\t}}")
    b.append(f"\t\t\t\t}}")
    b.append(f"\t\t\t}}")
    return [l + "\n" for l in b]


def lookup(target_form, display_field):
    """Return (type, extra_lines) for a lookup field."""
    return ("list", [
        f"values  = {target_form}.ID",
        f"displayformat = [{display_field}]",
        "allow new entries",
        "[",
        '\tdisplayname = "Add New"',
        "]",
        "sortorder = ascending",
        "height = 13px",
    ])


# ── TYPE SHORTCUTS ───────────────────────────────────────────
T = "text"
TA = "textarea"
DT = "date"
DTM = "datetime"
NUM = "number"
DEC = "decimal"
CB = "checkbox"
PL = "picklist"
EM = "email"


# ══════════════════════════════════════════════════════════════
# STEP 1: Upgrade chargeback_incidents — 18 new fields + status fix
# ══════════════════════════════════════════════════════════════
print("STEP 1: Upgrading chargeback_incidents fields...")

result = list(lines)

# 1a. Fix status picklist values (superset needed for blueprints)
for i, line in enumerate(result):
    if 'values = {"Resolved","Expired","Disputed","Open"}' in line:
        result[i] = line.replace(
            '{"Resolved","Expired","Disputed","Open"}',
            '{"Open","Under Review","Disputed","Resolved","Expired","Won","Lost"}'
        )
        print(f"  Fixed status picklist at line {i+1}")
        break

# 1b. Insert 18 new fields before the "actions" block in chargeback_incidents
#     Find "form chargeback_incidents", then its "actions" block
in_chargeback_form = False
actions_line = None
for i, line in enumerate(result):
    if re.match(r"^\t\tform chargeback_incidents\s*$", line.rstrip("\n")):
        in_chargeback_form = True
    if in_chargeback_form and line.strip() == "actions":
        actions_line = i
        break

if actions_line is None:
    print("ERROR: Could not find 'actions' block in chargeback_incidents", file=sys.stderr)
    sys.exit(1)

# Go back to find the blank line before "actions" (insertion point)
insert_at = actions_line
while insert_at > 0 and result[insert_at - 1].strip() == "":
    insert_at -= 1

new_fields = []
new_fields.extend(field_block("Dispute_Deadline", DT, "Dispute Deadline", ["alloweddays = 0,1,2,3,4,5,6"]))
new_fields.extend(field_block("Record_Type", T, "Record Type"))
new_fields.extend(field_block("Exchange_Rate", DEC, "Exchange Rate"))
new_fields.extend(field_block("Dispute_Reason", T, "Dispute Reason"))
new_fields.extend(field_block("Payment_Method", T, "Payment Method"))
new_fields.extend(field_block("CB_Scheme_Code", T, "CB Scheme Code"))
new_fields.extend(field_block("CB_Reason_Code", T, "CB Reason Code"))
new_fields.extend(field_block("Shopper_Country", T, "Shopper Country"))
new_fields.extend(field_block("Issuer_Country", T, "Issuer Country"))
new_fields.extend(field_block("Payment_Date", DT, "Payment Date", ["alloweddays = 0,1,2,3,4,5,6"]))
new_fields.extend(field_block("Payment_Currency", T, "Payment Currency"))
new_fields.extend(field_block("Payment_Amount", DEC, "Payment Amount"))
new_fields.extend(field_block("Dispute_Date", DT, "Dispute Date", ["alloweddays = 0,1,2,3,4,5,6"]))
new_fields.extend(field_block("Dispute_End_Date", DT, "Dispute End Date", ["alloweddays = 0,1,2,3,4,5,6"]))
new_fields.extend(field_block("Risk_Scoring", NUM, "Risk Scoring", ["maxchar = 19"]))
new_fields.extend(field_block("Shopper_Interaction", T, "Shopper Interaction"))
new_fields.extend(field_block("Dispute_PSP_Reference", T, "Dispute PSP Reference"))
new_fields.extend(field_block("Company_Account", T, "Company Account"))

result[insert_at:insert_at] = new_fields
offset = len(new_fields)
print(f"  Inserted {len(new_fields)} lines ({18} fields) at line {insert_at+1}")


# ══════════════════════════════════════════════════════════════
# STEP 2: Insert 8 new forms before the reports section
# ══════════════════════════════════════════════════════════════
print("STEP 2: Inserting 8 new forms...")

new_forms_data = [
    ("regional_config", "Regional Config", [
        ("merchant_account", T, "Merchant Account", []),
        ("region", T, "Region", []),
        ("default_currency", T, "Default Currency", []),
        ("default_lm_name", T, "Default LM Name", []),
        ("default_lm_email", EM, "Default LM Email", []),
    ]),
    ("merchant_platforms", "Merchant Platforms", [
        ("platform_name", T, "Platform Name", []),
        ("file_format", T, "File Format", []),
        ("delimiter", T, "Delimiter", []),
        ("region", T, "Region", []),
        ("is_active", CB, "Active", ["initial value = true"]),
    ]),
    ("currency_config", "Currency Config", [
        ("currency_code", T, "Currency Code", []),
        ("currency_name", T, "Currency Name", []),
        ("exchange_rate_source", T, "Exchange Rate Source", []),
    ]),
    ("dispute_reason_codes", "Dispute Reason Codes", [
        ("scheme", T, "Scheme", []),
        ("code", T, "Reason Code", []),
        ("description", TA, "Description", ["height = 100px"]),
        ("category", T, "Category", []),
    ]),
    ("lm_followups", "LM Followups", [
        ("incident", *lookup("chargeback_incidents", "incident_id"), "Incident"),
        ("followup_date", DT, "Followup Date", ["alloweddays = 0,1,2,3,4,5,6"]),
        ("followup_notes", TA, "Followup Notes", ["height = 100px"]),
        ("followed_up_by", T, "Followed Up By", []),
        ("evidence_gathered", CB, "Evidence Gathered", ["initial value = false"]),
    ]),
    ("dispute_submissions", "Dispute Submissions", [
        ("incident", *lookup("chargeback_incidents", "incident_id"), "Incident"),
        ("submission_date", DT, "Submission Date", ["alloweddays = 0,1,2,3,4,5,6"]),
        ("submitted_by", T, "Submitted By", []),
        ("dispute_reason_text", TA, "Dispute Reason", ["height = 100px"]),
        ("evidence_summary", TA, "Evidence Summary", ["height = 100px"]),
        ("expected_response_date", DT, "Expected Response Date", ["alloweddays = 0,1,2,3,4,5,6"]),
    ]),
    ("merchant_responses", "Merchant Responses", [
        ("dispute", *lookup("dispute_submissions", "submitted_by"), "Dispute"),
        ("response_date", DT, "Response Date", ["alloweddays = 0,1,2,3,4,5,6"]),
        ("response_status", PL, "Response Status", ['values = {"Accepted","Rejected","Partial","Information Requested"}']),
        ("additional_info", TA, "Additional Info", ["height = 100px"]),
        ("responded_by", T, "Responded By", []),
    ]),
    ("file_uploads", "File Uploads", [
        ("file_name", T, "File Name", []),
        ("platform_name", T, "Platform", []),
        ("incident", *lookup("chargeback_incidents", "incident_id"), "Incident"),
        ("processing_status", PL, "Processing Status", ['values = {"Pending","Processing","Completed"}']),
        ("records_found", NUM, "Records Found", ["initial value = 0"]),
        ("records_imported", NUM, "Records Imported", ["initial value = 0"]),
    ]),
]

# Fix lookup fields — *lookup() unpacks as (name, "list", [extra_lines], "Display")
# where fdisplay is actually the extra lines list and fextra is the real display name
fixed_forms = []
for form_name, form_display, fields in new_forms_data:
    fixed_fields = []
    for f in fields:
        if len(f) == 4:
            fname, ftype, fdisplay, fextra = f
            if ftype == "list" and isinstance(fdisplay, list):
                # Lookup field: fdisplay has extra lines, fextra has display name
                fixed_fields.append((fname, ftype, fextra, fdisplay))
            else:
                fixed_fields.append((fname, ftype, fdisplay, fextra))
        else:
            fixed_fields.append(f)
    fixed_forms.append((form_name, form_display, fixed_fields))

# Find the closing brace of the forms { } block (just before "reports")
# New forms must go INSIDE forms { }, not between } and reports
forms_insert = None
for i, line in enumerate(result):
    if line.strip() == "reports" and i > 100:
        # Walk backwards to find the } that closes the forms block
        for j in range(i - 1, 0, -1):
            if result[j].strip() == "}":
                forms_insert = j  # Insert before this closing }
                break
        break

if forms_insert is None:
    print("ERROR: Could not find forms closing brace", file=sys.stderr)
    sys.exit(1)

new_form_lines = []
for form_name, form_display, fields in fixed_forms:
    new_form_lines.extend(form_block(form_name, form_display, fields))

result[forms_insert:forms_insert] = new_form_lines
offset += len(new_form_lines)
print(f"  Inserted {len(new_form_lines)} lines ({len(fixed_forms)} forms)")

new_form_names = [f[0] for f in fixed_forms]


# ══════════════════════════════════════════════════════════════
# STEP 3: Add 6 new reports before pages section
# ══════════════════════════════════════════════════════════════
print("STEP 3: Adding 6 new reports...")

# Report definitions — 4 from original splice + 2 new filtered reports
new_report_defs = [
    ("regional_config_Report", "Regional Config", "regional_config",
     ["merchant_account", "region", "default_currency", "default_lm_name", "default_lm_email"],
     ""),
    ("dispute_reason_codes_Report", "Dispute Reason Codes", "dispute_reason_codes",
     ["scheme", "code", "description", "category"],
     ""),
    ("dispute_submissions_Report", "Disputes", "dispute_submissions",
     ["incident", "submission_date", "submitted_by", "dispute_reason_text", "expected_response_date"],
     ""),
    ("file_uploads_Report", "File Uploads", "file_uploads",
     ["file_name", "platform_name", "processing_status", "records_found", "records_imported"],
     ""),
    ("Open_Chargebacks", "Open Chargebacks", "chargeback_incidents",
     ["psp_reference", "platform", "merchant_account", "amount_usd", "incident_date", "days_remaining", "assigned_lm"],
     'status == "Open" || status == "Under Review"'),
    ("Expiring_Soon", "Expiring Soon", "chargeback_incidents",
     ["psp_reference", "platform", "amount_usd", "days_remaining", "assigned_lm", "Dispute_Deadline"],
     'days_remaining <= 5 && days_remaining > 0 && (status == "Open" || status == "Under Review")'),
]

new_report_names = [r[0] for r in new_report_defs]

new_report_lines = []
for rpt_name, rpt_display, rpt_form, rpt_cols, rpt_filter in new_report_defs:
    new_report_lines.extend(report_block(rpt_name, rpt_display, rpt_form, rpt_cols, rpt_filter))

# Find the closing brace of the reports { } block (just before "pages")
# New reports must go INSIDE reports { }, not between } and pages
for i, line in enumerate(result):
    if line.strip() == "pages" and i > 100 + offset:
        # Walk backwards to find the } that closes the reports block
        for j in range(i - 1, 0, -1):
            if result[j].strip() == "}":
                result[j:j] = new_report_lines
                offset += len(new_report_lines)
                print(f"  Inserted {len(new_report_lines)} lines ({len(new_report_defs)} reports)")
                break
        break


# ══════════════════════════════════════════════════════════════
# STEP 4: Wire in Deluge form workflows
# ══════════════════════════════════════════════════════════════
if args.no_scripts:
    print("STEP 4: SKIPPED (--no-scripts)")
else:
    print("STEP 4: Wiring in Deluge form workflows + scheduled scripts...")

    wf_scripts = [
        {
            "link_name": "chargeback_incident_on_success",
            "display_name": "Chargeback Incident On Success",
            "form": "chargeback_incidents",
            "record_event": "on add",
            "event_type": "on success",
            "path": PROJECT_ROOT / "src" / "deluge" / "form-workflows" / "chargeback_incident.on_success.dg",
        },
        {
            "link_name": "dispute_submission_on_success",
            "display_name": "Dispute Submission On Success",
            "form": "dispute_submissions",
            "record_event": "on add",
            "event_type": "on success",
            "path": PROJECT_ROOT / "src" / "deluge" / "form-workflows" / "dispute_submission.on_success.dg",
        },
    ]

    sched_scripts = [
        {
            "link_name": "auto_alert_25_days",
            "display_name": "Auto Alert 25 Days",
            "form": "chargeback_incidents",
            "path": PROJECT_ROOT / "src" / "deluge" / "scheduled" / "auto_alert_25_days.dg",
        },
        {
            "link_name": "daily_file_processing",
            "display_name": "Daily File Processing",
            "form": "chargeback_incidents",
            "path": PROJECT_ROOT / "src" / "deluge" / "scheduled" / "daily_file_processing.dg",
        },
        {
            "link_name": "currency_conversion_batch",
            "display_name": "Currency Conversion Batch",
            "form": "chargeback_incidents",
            "path": PROJECT_ROOT / "src" / "deluge" / "scheduled" / "currency_conversion_batch.dg",
        },
        {
            "link_name": "data_cleansing_scheduled",
            "display_name": "Data Cleansing Scheduled",
            "form": "chargeback_incidents",
            "path": PROJECT_ROOT / "src" / "deluge" / "scheduled" / "data_cleansing_scheduled.dg",
        },
    ]

    # Find the workflow { block, then the blueprint block inside it
    workflow_line = None
    blueprint_line = None
    for i, line in enumerate(result):
        if line.strip() == "workflow" and i > 500:
            workflow_line = i
        if workflow_line and line.strip() == "blueprint" and i > workflow_line:
            blueprint_line = i
            break

    if workflow_line is None or blueprint_line is None:
        print("ERROR: Could not find workflow/blueprint blocks", file=sys.stderr)
        sys.exit(1)

    # Build form workflow block
    wf_lines = []
    wf_lines.append("\t\tform\n")
    wf_lines.append("\t\t{\n")
    for wf in wf_scripts:
        code = read_deluge_script(wf["path"])
        wf_lines.extend(workflow_block(
            wf["link_name"], wf["display_name"], wf["form"],
            wf["record_event"], wf["event_type"], code
        ))
    wf_lines.append("\t\t}\n")
    wf_lines.append("\n")

    # Build schedule block
    wf_lines.append("\t\tschedule\n")
    wf_lines.append("\t\t{\n")
    for sched in sched_scripts:
        code = read_deluge_script(sched["path"])
        wf_lines.extend(schedule_block(
            sched["link_name"], sched["display_name"], sched["form"], code
        ))
    wf_lines.append("\t\t}\n")
    wf_lines.append("\n")

    # Insert before the blueprint line
    result[blueprint_line:blueprint_line] = wf_lines
    offset += len(wf_lines)
    print(f"  Inserted {len(wf_lines)} lines (2 form workflows + 4 scheduled scripts)")


# ══════════════════════════════════════════════════════════════
# STEP 5: Add web > reports entries for new reports
# ══════════════════════════════════════════════════════════════
print("STEP 5: Adding web > reports entries...")

# Map report names to their columns for web blocks
report_columns_map = {r[0]: r[3] for r in new_report_defs}

# Find web > reports closing brace
in_web = False
in_web_reports = False
web_reports_end = None
for i, line in enumerate(result):
    if line.strip() == "web" and i > 1500:
        in_web = True
    if in_web and line.strip() == "reports":
        in_web_reports = True
        depth = 0
        for j in range(i, len(result)):
            depth += result[j].count("{") - result[j].count("}")
            if depth <= 0 and j > i:
                web_reports_end = j
                break
        break

if web_reports_end:
    web_rpt_lines = []
    for rpt_name, rpt_display, rpt_form, rpt_cols, rpt_filter in new_report_defs:
        web_rpt_lines.extend(web_report_block(rpt_name, rpt_cols))

    result[web_reports_end:web_reports_end] = web_rpt_lines
    offset += len(web_rpt_lines)
    print(f"  Inserted {len(web_rpt_lines)} lines ({len(new_report_defs)} web report entries)")
else:
    print("  WARNING: Could not find web > reports block, skipping")


# ══════════════════════════════════════════════════════════════
# STEP 6: Add web > forms entries for new forms
# ══════════════════════════════════════════════════════════════
print("STEP 6: Adding web/phone/tablet form entries...")

web_form_lines = []
for fn in new_form_names:
    web_form_lines.append(f"\t\t\tform {fn}\n")
    web_form_lines.append(f"\t\t\t{{\n")
    web_form_lines.append(f"\t\t\t\tlabel placement = left\n")
    web_form_lines.append(f"\t\t\t}}\n")

# Find web > forms closing brace
in_web = False
for i, line in enumerate(result):
    if line.strip() == "web" and i > 1500:
        in_web = True
    if in_web and line.strip() == "forms":
        depth = 0
        for j in range(i, len(result)):
            depth += result[j].count("{") - result[j].count("}")
            if depth <= 0 and j > i:
                result[j:j] = web_form_lines
                offset += len(web_form_lines)
                print(f"  Inserted {len(web_form_lines)} web form lines")
                break
        break


# ══════════════════════════════════════════════════════════════
# STEP 7: Add menu sections
# ══════════════════════════════════════════════════════════════
print("STEP 7: Adding menu sections...")

# Map of forms that have reports for menu linking
form_report_map = {
    "regional_config": "regional_config_Report",
    "dispute_reason_codes": "dispute_reason_codes_Report",
    "dispute_submissions": "dispute_submissions_Report",
    "file_uploads": "file_uploads_Report",
}

menu_lines = []
menu_lines.append(f"\t\t\t\tsection Section_Config\n")
menu_lines.append(f"\t\t\t\t{{\n")
menu_lines.append(f'\t\t\t\t\tdisplayname = "Configuration"\n')
menu_lines.append(f'\t\t\t\t\ticon = "design-app"\n')
for fn in ["regional_config", "merchant_platforms", "currency_config", "dispute_reason_codes"]:
    menu_lines.append(f"\t\t\t\t\tform  {fn}\n")
    menu_lines.append(f"\t\t\t\t\t{{\n")
    menu_lines.append(f'\t\t\t\t\t\ticon = "ui-1-bold-add"\n')
    menu_lines.append(f"\t\t\t\t\t}}\n")
    if fn in form_report_map:
        menu_lines.append(f"\t\t\t\t\treport {form_report_map[fn]}\n")
        menu_lines.append(f"\t\t\t\t\t{{\n")
        menu_lines.append(f'\t\t\t\t\t\ticon = "travel-world"\n')
        menu_lines.append(f"\t\t\t\t\t}}\n")
menu_lines.append(f"\t\t\t\t}}\n")

menu_lines.append(f"\t\t\t\tsection Section_Disputes\n")
menu_lines.append(f"\t\t\t\t{{\n")
menu_lines.append(f'\t\t\t\t\tdisplayname = "Disputes & Followups"\n')
menu_lines.append(f'\t\t\t\t\ticon = "business-currency-dollar"\n')
for fn in ["lm_followups", "dispute_submissions", "merchant_responses", "file_uploads"]:
    menu_lines.append(f"\t\t\t\t\tform  {fn}\n")
    menu_lines.append(f"\t\t\t\t\t{{\n")
    menu_lines.append(f'\t\t\t\t\t\ticon = "ui-1-bold-add"\n')
    menu_lines.append(f"\t\t\t\t\t}}\n")
    if fn in form_report_map:
        menu_lines.append(f"\t\t\t\t\treport {form_report_map[fn]}\n")
        menu_lines.append(f"\t\t\t\t\t{{\n")
        menu_lines.append(f'\t\t\t\t\t\ticon = "travel-world"\n')
        menu_lines.append(f"\t\t\t\t\t}}\n")
menu_lines.append(f"\t\t\t\t}}\n")

menu_lines.append(f"\t\t\t\tsection Section_Monitoring\n")
menu_lines.append(f"\t\t\t\t{{\n")
menu_lines.append(f'\t\t\t\t\tdisplayname = "Monitoring"\n')
menu_lines.append(f'\t\t\t\t\ticon = "tech-desktop-pulse"\n')
menu_lines.append(f"\t\t\t\t\treport Open_Chargebacks\n")
menu_lines.append(f"\t\t\t\t\t{{\n")
menu_lines.append(f'\t\t\t\t\t\ticon = "ui-1-circle-bold-warning"\n')
menu_lines.append(f"\t\t\t\t\t}}\n")
menu_lines.append(f"\t\t\t\t\treport Expiring_Soon\n")
menu_lines.append(f"\t\t\t\t\t{{\n")
menu_lines.append(f'\t\t\t\t\t\ticon = "ui-1-circle-bold-remove"\n')
menu_lines.append(f"\t\t\t\t\t}}\n")
menu_lines.append(f"\t\t\t\t}}\n")

# Find last section in menu (ZC_ or SharedAnalytics)
for i in range(len(result) - 1, 0, -1):
    if "section ZC_" in result[i] or "SharedAnalytics" in result[i]:
        depth = 0
        for j in range(i, len(result)):
            depth += result[j].count("{") - result[j].count("}")
            if depth <= 0 and j > i:
                result[j+1:j+1] = menu_lines
                offset += len(menu_lines)
                print(f"  Inserted {len(menu_lines)} menu lines")
                break
        break


# ══════════════════════════════════════════════════════════════
# STEP 8: Insert phone/tablet form entries
# ══════════════════════════════════════════════════════════════
print("STEP 8: Adding phone/tablet form entries...")

phone_lines = []
for fn in new_form_names:
    phone_lines.append(f"\t\t\tform {fn}\n")
    phone_lines.append(f"\t\t\t{{\n")
    phone_lines.append(f"\t\t\t\tlabel placement = auto\n")
    phone_lines.append(f"\t\t\t}}\n")

for section_name in ["phone", "tablet"]:
    for i, line in enumerate(result):
        if line.strip() == section_name:
            for j in range(i, min(i + 5, len(result))):
                if result[j].strip() == "forms":
                    depth = 0
                    for k in range(j, len(result)):
                        depth += result[k].count("{") - result[k].count("}")
                        if depth <= 0 and k > j:
                            result[k:k] = list(phone_lines)
                            offset += len(phone_lines)
                            break
                    break
            break


# ══════════════════════════════════════════════════════════════
# WRITE OUTPUT + VALIDATION
# ══════════════════════════════════════════════════════════════
output = "".join(result)
with open(OUTPUT, "w", encoding="utf-8", newline="\n") as f:
    f.write(output)

# Validation summary
all_forms = re.findall(r"^\t\tform (\w+)", output, re.MULTILINE)
unique_forms = sorted(set(all_forms))
workflow_count = len(re.findall(r"custom deluge script", output))
schedule_count = len(re.findall(r"type =  schedule", output))
blueprint_count = len(re.findall(r"type = Blueprint", output))
report_count = len(re.findall(r"^\t\tlist \w+|^\t\tkanban \w+", output, re.MULTILINE))

print(f"\n{'='*60}")
print(f"OUTPUT: {OUTPUT}")
print(f"Lines:  {len(result)}")
print(f"Forms:  {len(unique_forms)} -> {unique_forms}")
print(f"Reports:       {report_count}")
print(f"Workflows:     {workflow_count}")
print(f"Schedules:     {schedule_count}")
print(f"Blueprints:    {blueprint_count}")

# Sanity checks
assert len(unique_forms) == 11, f"Expected 11 forms, got {len(unique_forms)}"
assert "invoices" in unique_forms, "Invoices form missing!"
assert "chargeback_incidents" in unique_forms, "Chargeback incidents form missing!"
if not args.no_scripts:
    assert workflow_count == 2, f"Expected 2 workflows, got {workflow_count}"
    assert schedule_count == 4, f"Expected 4 schedules, got {schedule_count}"
assert blueprint_count == 2, f"Expected 2 blueprints, got {blueprint_count}"
print("\nAll assertions passed!")
