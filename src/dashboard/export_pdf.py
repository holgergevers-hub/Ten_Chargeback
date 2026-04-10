"""Generate a PDF snapshot of the Ten Group Chargeback Risk Dashboard."""

import json
import pathlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.patches as mpatches
import numpy as np

# ── Paths ────────────────────────────────────────────────────────────────
HERE = pathlib.Path(__file__).resolve().parent
DATA_PATHS = [HERE / "dashboard_data.json", HERE.parent.parent / "data" / "clean" / "dashboard_data.json"]

# ── Theme (matches the dark dashboard CSS) ───────────────────────────────
BG       = "#0f172a"
CARD_BG  = "#1e293b"
TEXT     = "#f1f5f9"
TEXT_SEC  = "#94a3b8"
TEXT_MUT  = "#64748b"
BORDER   = "#334155"
BLUE     = "#3b82f6"
GREEN    = "#22c55e"
RED      = "#ef4444"
AMBER    = "#f59e0b"
PURPLE   = "#a855f7"
CYAN     = "#06b6d4"
PINK     = "#ec4899"
INDIGO   = "#6366f1"
TEAL     = "#14b8a6"
CHART_COLORS = [BLUE, GREEN, AMBER, RED, PURPLE, CYAN, PINK, INDIGO, TEAL]

KPI_GRADIENTS = [
    ("#1e40af", BLUE),
    ("#991b1b", RED),
    ("#92400e", AMBER),
    ("#166534", GREEN),
]


def fmt_usd(v):
    return f"${v:,.0f}"


def fmt_pct(v, total):
    return f"{v / total * 100:.1f}%"


def load_data():
    for p in DATA_PATHS:
        if p.exists():
            return json.loads(p.read_text())
    raise FileNotFoundError("dashboard_data.json not found")


def rounded_rect(ax, xy, width, height, radius, color):
    """Draw a rounded rectangle on an axes."""
    fancy = mpatches.FancyBboxPatch(
        xy, width, height,
        boxstyle=f"round,pad=0,rounding_size={radius}",
        facecolor=color, edgecolor="none", zorder=0,
    )
    ax.add_patch(fancy)


def draw_kpi_card(ax, label, value, detail, bg_color):
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_facecolor(bg_color)
    ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.text(0.08, 0.78, label.upper(), fontsize=7, fontweight="500",
            color=TEXT, alpha=0.85, va="top", fontfamily="sans-serif")
    ax.text(0.08, 0.42, value, fontsize=18, fontweight="bold",
            color=TEXT, va="center", fontfamily="sans-serif")
    ax.text(0.08, 0.12, detail, fontsize=6.5, color=TEXT, alpha=0.7,
            va="bottom", fontfamily="sans-serif")


def build_pdf(data, out_path):
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
        "text.color": TEXT,
        "axes.facecolor": CARD_BG,
        "axes.edgecolor": BORDER,
        "axes.labelcolor": TEXT_SEC,
        "xtick.color": TEXT_SEC,
        "ytick.color": TEXT_SEC,
        "figure.facecolor": BG,
    })

    with PdfPages(str(out_path)) as pdf:
        # ═══════════════ PAGE 1 ═══════════════
        fig = plt.figure(figsize=(16.54, 11.69))  # A3 landscape in inches
        fig.set_facecolor(BG)

        # Title
        fig.text(0.04, 0.96, "Ten Group — Chargeback Risk Dashboard",
                 fontsize=22, fontweight="bold", color=TEXT, va="top")
        fig.text(0.04, 0.935, "CFO / COO Executive Summary  •  Data Period: Jan 2024 – Dec 2024",
                 fontsize=10, color=TEXT_SEC, va="top")
        # Thin line under header
        line_ax = fig.add_axes([0.04, 0.925, 0.92, 0.001])
        line_ax.set_facecolor(BORDER)
        line_ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
        for s in line_ax.spines.values():
            s.set_visible(False)

        # ── KPI cards ─────────────────────────────────────────
        total = data["total_usd"]
        count = data["total_count"]
        cb_amt = next((c["amount_usd"] for c in data["by_category"] if c["category"] == "Chargeback"), 0)
        fraud_amt = next((c["amount_usd"] for c in data["by_category"] if c["category"] == "Fraud"), 0)
        fraud_cnt = next((c["count"] for c in data["by_category"] if c["category"] == "Fraud"), 0)
        rec_amt = next((c["amount_usd"] for c in data["by_category"] if c["category"] == "Recovered"), 0)
        rec_rate = f"{rec_amt / total * 100:.1f}%" if total > 0 else "0.0%"

        kpis = [
            ("Total Chargeback Exposure", fmt_usd(total), f"{count} disputes across 3 platforms", KPI_GRADIENTS[0][1]),
            ("Chargeback Amount", fmt_usd(cb_amt), f"{fmt_pct(cb_amt, total)} of total exposure", KPI_GRADIENTS[1][1]),
            ("Fraud Notifications", fmt_usd(fraud_amt), f"{fraud_cnt} fraud alerts", KPI_GRADIENTS[2][1]),
            ("Recovery Rate", rec_rate, f"{fmt_usd(rec_amt)} recovered", KPI_GRADIENTS[3][1]),
        ]

        for i, (label, value, detail, color) in enumerate(kpis):
            ax = fig.add_axes([0.04 + i * 0.235, 0.82, 0.22, 0.09])
            draw_kpi_card(ax, label, value, detail, color)

        # ── Monthly Trend (wide chart) ────────────────────────
        ax_trend = fig.add_axes([0.04, 0.46, 0.92, 0.33])
        months = [m["month"] for m in data["monthly_trend"]]
        amounts = [m["amount_usd"] for m in data["monthly_trend"]]
        counts = [m["count"] for m in data["monthly_trend"]]
        x = np.arange(len(months))

        ax_trend.bar(x, amounts, color=BLUE, alpha=0.7, width=0.6, label="Amount (USD)", zorder=2)
        ax_trend.set_ylabel("Amount (USD)", fontsize=9)
        ax_trend.set_xticks(x)
        ax_trend.set_xticklabels(months, fontsize=8)
        ax_trend.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: fmt_usd(v)))
        ax_trend.tick_params(axis="y", labelsize=8)
        ax_trend.grid(axis="y", color=BORDER, linewidth=0.5, zorder=0)
        ax_trend.set_title("Monthly Chargeback Trend", fontsize=11, color=TEXT_SEC, loc="left", pad=10)

        ax2 = ax_trend.twinx()
        ax2.plot(x, counts, color=AMBER, marker="o", markersize=5, linewidth=2, label="Count", zorder=3)
        ax2.fill_between(x, counts, alpha=0.1, color=AMBER)
        ax2.set_ylabel("Count", fontsize=9, color=TEXT_SEC)
        ax2.tick_params(axis="y", labelsize=8, colors=TEXT_SEC)
        ax2.spines["right"].set_color(BORDER)
        ax2.spines["left"].set_color(BORDER)
        ax2.spines["top"].set_visible(False)
        ax_trend.spines["top"].set_visible(False)

        handles = [mpatches.Patch(color=BLUE, alpha=0.7, label="Amount (USD)"),
                   plt.Line2D([0], [0], color=AMBER, marker="o", label="Count")]
        ax_trend.legend(handles=handles, fontsize=8, loc="upper right",
                        facecolor=CARD_BG, edgecolor=BORDER, labelcolor=TEXT_SEC)

        # ── Row: By Platform + By Category ────────────────────
        # By Platform (horizontal bar)
        ax_plat = fig.add_axes([0.04, 0.08, 0.43, 0.32])
        plat_labels = [p["platform"] for p in data["by_platform"]]
        plat_vals = [p["amount_usd"] for p in data["by_platform"]]
        plat_colors = [BLUE, GREEN, PURPLE]
        y_plat = np.arange(len(plat_labels))
        ax_plat.barh(y_plat, plat_vals, color=plat_colors[:len(plat_labels)], height=0.5, zorder=2)
        ax_plat.set_yticks(y_plat)
        ax_plat.set_yticklabels(plat_labels, fontsize=9)
        ax_plat.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: fmt_usd(v)))
        ax_plat.tick_params(axis="x", labelsize=8)
        ax_plat.set_title("By Platform", fontsize=11, color=TEXT_SEC, loc="left", pad=10)
        ax_plat.grid(axis="x", color=BORDER, linewidth=0.5, zorder=0)
        ax_plat.invert_yaxis()
        ax_plat.spines["top"].set_visible(False)
        ax_plat.spines["right"].set_visible(False)

        # By Category (doughnut)
        ax_cat = fig.add_axes([0.55, 0.08, 0.38, 0.32])
        cat_labels = [c["category"] for c in data["by_category"]]
        cat_vals = [c["amount_usd"] for c in data["by_category"]]
        cat_colors = [RED, AMBER, GREEN, BLUE]
        wedges, texts, autotexts = ax_cat.pie(
            cat_vals, labels=cat_labels, colors=cat_colors[:len(cat_labels)],
            autopct=lambda p: f"{p:.1f}%", startangle=90,
            pctdistance=0.78, wedgeprops=dict(width=0.4, edgecolor=BG),
            textprops=dict(color=TEXT_SEC, fontsize=8),
        )
        for at in autotexts:
            at.set_fontsize(7)
            at.set_color(TEXT)
        ax_cat.set_title("By Category", fontsize=11, color=TEXT_SEC, loc="left", pad=10)

        pdf.savefig(fig)
        plt.close(fig)

        # ═══════════════ PAGE 2 ═══════════════
        fig2 = plt.figure(figsize=(16.54, 11.69))
        fig2.set_facecolor(BG)
        fig2.text(0.04, 0.96, "Ten Group — Chargeback Risk Dashboard (continued)",
                  fontsize=18, fontweight="bold", color=TEXT, va="top")
        line_ax2 = fig2.add_axes([0.04, 0.94, 0.92, 0.001])
        line_ax2.set_facecolor(BORDER)
        line_ax2.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
        for s in line_ax2.spines.values():
            s.set_visible(False)

        # ── By Region (bar) ───────────────────────────────────
        ax_reg = fig2.add_axes([0.04, 0.62, 0.43, 0.28])
        reg_labels = [r["region"] for r in data["by_region"]]
        reg_vals = [r["amount_usd"] for r in data["by_region"]]
        x_reg = np.arange(len(reg_labels))
        ax_reg.bar(x_reg, reg_vals, color=CHART_COLORS[:len(reg_labels)], width=0.5, zorder=2)
        ax_reg.set_xticks(x_reg)
        ax_reg.set_xticklabels(reg_labels, fontsize=9)
        ax_reg.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: fmt_usd(v)))
        ax_reg.tick_params(axis="y", labelsize=8)
        ax_reg.set_title("By Region (USD)", fontsize=11, color=TEXT_SEC, loc="left", pad=10)
        ax_reg.grid(axis="y", color=BORDER, linewidth=0.5, zorder=0)
        ax_reg.spines["top"].set_visible(False)
        ax_reg.spines["right"].set_visible(False)

        # ── By Currency (doughnut) ────────────────────────────
        ax_cur = fig2.add_axes([0.55, 0.62, 0.38, 0.28])
        cur_labels = [c["currency"] for c in data["by_currency"]]
        cur_vals = [c["amount_original"] for c in data["by_currency"]]
        wedges2, texts2, autotexts2 = ax_cur.pie(
            cur_vals, labels=cur_labels, colors=CHART_COLORS[:len(cur_labels)],
            autopct=lambda p: f"{p:.1f}%", startangle=90,
            pctdistance=0.78, wedgeprops=dict(width=0.4, edgecolor=BG),
            textprops=dict(color=TEXT_SEC, fontsize=8),
        )
        for at in autotexts2:
            at.set_fontsize(7)
            at.set_color(TEXT)
        ax_cur.set_title("By Currency (Original)", fontsize=11, color=TEXT_SEC, loc="left", pad=10)

        # ── Top Merchants table ───────────────────────────────
        ax_tbl1 = fig2.add_axes([0.04, 0.30, 0.92, 0.26])
        ax_tbl1.set_facecolor(CARD_BG)
        ax_tbl1.set_xlim(0, 1)
        ax_tbl1.set_ylim(0, 1)
        ax_tbl1.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
        for s in ax_tbl1.spines.values():
            s.set_color(BORDER)
        ax_tbl1.set_title("Top Merchants by Chargeback Amount (USD)", fontsize=11,
                          color=TEXT_SEC, loc="left", pad=10)

        headers = ["Merchant Account", "Platform", "Count", "Amount (USD)", "% of Total"]
        col_x = [0.03, 0.28, 0.45, 0.58, 0.80]
        y_start = 0.88
        row_h = 0.12

        for j, h in enumerate(headers):
            ax_tbl1.text(col_x[j], y_start, h, fontsize=7.5, fontweight="bold",
                         color=TEXT_MUT, va="center", transform=ax_tbl1.transAxes)
        ax_tbl1.plot([0.02, 0.98], [y_start - row_h * 0.4]*2, color=BORDER, linewidth=0.5)

        for i, m in enumerate(data["by_merchant"]):
            y = y_start - (i + 1) * row_h
            vals = [m["merchant"], m["platform"], str(m["count"]),
                    fmt_usd(m["amount_usd"]), fmt_pct(m["amount_usd"], total)]
            for j, v in enumerate(vals):
                ax_tbl1.text(col_x[j], y, v, fontsize=8, color=TEXT,
                             va="center", transform=ax_tbl1.transAxes)
            if i < len(data["by_merchant"]) - 1:
                ax_tbl1.plot([0.02, 0.98], [y - row_h * 0.4]*2, color=BORDER, linewidth=0.3)

        # ── Record Type Breakdown table ───────────────────────
        ax_tbl2 = fig2.add_axes([0.04, 0.03, 0.92, 0.22])
        ax_tbl2.set_facecolor(CARD_BG)
        ax_tbl2.set_xlim(0, 1)
        ax_tbl2.set_ylim(0, 1)
        ax_tbl2.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
        for s in ax_tbl2.spines.values():
            s.set_color(BORDER)
        ax_tbl2.set_title("Record Type Breakdown", fontsize=11,
                          color=TEXT_SEC, loc="left", pad=10)

        headers2 = ["Record Type", "Count", "Amount (USD)", "% of Total"]
        col_x2 = [0.03, 0.35, 0.55, 0.80]
        y_start2 = 0.85
        row_h2 = 0.14

        for j, h in enumerate(headers2):
            ax_tbl2.text(col_x2[j], y_start2, h, fontsize=7.5, fontweight="bold",
                         color=TEXT_MUT, va="center", transform=ax_tbl2.transAxes)
        ax_tbl2.plot([0.02, 0.98], [y_start2 - row_h2 * 0.4]*2, color=BORDER, linewidth=0.5)

        for i, t in enumerate(data["by_record_type"]):
            y = y_start2 - (i + 1) * row_h2
            vals = [t["type"], str(t["count"]),
                    fmt_usd(t["amount_usd"]), fmt_pct(t["amount_usd"], total)]
            for j, v in enumerate(vals):
                ax_tbl2.text(col_x2[j], y, v, fontsize=8, color=TEXT,
                             va="center", transform=ax_tbl2.transAxes)
            if i < len(data["by_record_type"]) - 1:
                ax_tbl2.plot([0.02, 0.98], [y - row_h2 * 0.4]*2, color=BORDER, linewidth=0.3)

        pdf.savefig(fig2)
        plt.close(fig2)

    print(f"PDF saved: {out_path}")


if __name__ == "__main__":
    data = load_data()
    out = HERE / "Ten_Group_Chargeback_Dashboard.pdf"
    build_pdf(data, out)
