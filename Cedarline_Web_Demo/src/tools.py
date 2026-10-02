import json
import sqlite3
from pathlib import Path
from datetime import date

DATABASE = Path(__file__).resolve().parents[1] / "data" / "cedarline.db"


def get_job_margin_report(branch_id=None):
    """Report completed-job margins, optionally filtered by branch."""
    if not DATABASE.is_file():
        raise FileNotFoundError("Run build_database.py first.")

    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row

    try:
        rows = connection.execute("""
            SELECT
                job_id,
                branch_id,
                revenue_cents,
                labor_cost_cents,
                material_cost_cents,
                revenue_cents
                    - labor_cost_cents
                    - material_cost_cents AS profit_cents
            FROM jobs
            WHERE status = 'completed'
              AND (? IS NULL OR branch_id = ?)
            ORDER BY job_id
        """, (branch_id, branch_id)).fetchall()
    finally:
        connection.close()

    findings = []
    incomplete_jobs = []
    revenue_total = 0
    cost_total = 0
    included_count = 0

    for row in rows:
        required = (
            row["revenue_cents"],
            row["labor_cost_cents"],
            row["material_cost_cents"],
        )

        if any(value is None for value in required):
            missing_fields = [
                field
                for field in (
                    "revenue_cents",
                    "labor_cost_cents",
                    "material_cost_cents",
                )
                if row[field] is None
            ]

            incomplete_jobs.append({
                "job_id": row["job_id"],
                "job_status": "completed",
                "missing_fields": missing_fields,
                "exclusion_reason": "Missing financial values",
            })
            continue

        revenue = row["revenue_cents"]
        profit = row["profit_cents"]
        cost = (
            row["labor_cost_cents"]
            + row["material_cost_cents"]
        )

        revenue_total += revenue
        cost_total += cost
        included_count += 1

        margin_percent = (
            round(profit / revenue * 100, 2)
            if revenue != 0 else None
        )

        # Compare unrounded amounts against the 30% threshold.
        needs_review = (
            revenue <= 0
            or profit * 100 < revenue * 30
        )

        if needs_review:
            findings.append({
                "job_id": row["job_id"],
                "branch_id": row["branch_id"],
                "gross_profit_cents": profit,
                "gross_margin_percent": margin_percent,
                "reason": (
                    "Nonpositive revenue requires review"
                    if revenue <= 0
                    else "Margin below 30%"
                ),
            })

    profit_total = revenue_total - cost_total

    return {
                "report_scope": (
            "Completed jobs with known revenue, labor, and material costs"
        ),
        "margin_definition": (
            "(Revenue - labor cost - material cost) / revenue"
        ),
        "overall_margin_target_percent": None,
        "interpretation_limits": [
            "No approved overall margin target is available.",
            "Do not classify overall margin as healthy or unhealthy.",
            "The 30% threshold applies only to individual job review.",
            "This report does not establish causes of low margins.",
            "Overhead is not included in this gross-margin calculation.",
        ],
        "branch_filter": branch_id,
        "included_completed_job_count": included_count,
        "revenue_cents": revenue_total,
        "direct_cost_cents": cost_total,
        "gross_profit_cents": profit_total,
        "gross_margin_percent": (
            round(profit_total / revenue_total * 100, 2)
            if revenue_total != 0 else None
        ),
        "margin_investigations": findings,
        "incomplete_jobs": incomplete_jobs,
    }

def get_overdue_invoices(as_of_date):
    """Return unpaid balances due before the supplied YYYY-MM-DD date."""
    report_date = date.fromisoformat(as_of_date)

    if not DATABASE.is_file():
        raise FileNotFoundError("Run build_database.py first.")

    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row

    try:
        rows = connection.execute("""
            SELECT
                i.invoice_id,
                i.job_id,
                j.branch_id,
                i.due_date,
                i.amount_cents,
                i.paid_amount_cents,
                i.amount_cents - i.paid_amount_cents AS balance_cents
            FROM invoices AS i
            JOIN jobs AS j ON j.job_id = i.job_id
            WHERE i.due_date < ?
              AND i.amount_cents - i.paid_amount_cents > 0
            ORDER BY i.due_date, i.invoice_id
        """, (report_date.isoformat(),)).fetchall()
    finally:
        connection.close()

    invoices = []

    for row in rows:
        invoice = dict(row)
        invoice["days_overdue"] = (
            report_date - date.fromisoformat(row["due_date"])
        ).days
        invoices.append(invoice)

    return {
        "as_of_date": report_date.isoformat(),
        "definition": (
            "Positive unpaid balance with due date before as_of_date"
        ),
        "overdue_invoice_count": len(invoices),
        "total_overdue_balance_cents": sum(
            invoice["balance_cents"] for invoice in invoices
        ),
        "invoices": invoices,
        "action_limits": [
            "Collection review only; this tool cannot send messages.",
            "Customer contact details are not available.",
        ],
    }

if __name__ == "__main__":
    print(json.dumps(get_job_margin_report(), indent=2))