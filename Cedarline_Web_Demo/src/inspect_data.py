"""Deterministic inspection baseline. This is not an AI agent."""
import csv
import json
from datetime import date
from decimal import Decimal
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / 'data'

def read(name):
    with (DATA / name).open(newline='') as handle:
        return list(csv.DictReader(handle))

def main():
    jobs = read('jobs.csv')
    revenue = Decimal('0')
    cost = Decimal('0')
    findings = []
    incomplete = []
    for row in jobs:
        if row['status'] != 'completed':
            continue
        if any(row[key] == '' for key in ('revenue', 'labor_cost', 'material_cost')):
            incomplete.append(row['job_id'])
            continue
        amount = Decimal(row['revenue'])
        direct = Decimal(row['labor_cost']) + Decimal(row['material_cost'])
        margin = (amount - direct) / amount if amount else None
        revenue += amount
        cost += direct
        if margin is None or margin < Decimal('0.30'):
            findings.append({'job_id': row['job_id'], 'profit': str(amount-direct),
                             'margin': str(margin) if margin is not None else None})
    as_of = date(2026, 10, 2)
    overdue = []
    for row in read('invoices.csv'):
        balance = Decimal(row['amount']) - Decimal(row['paid_amount'])
        if date.fromisoformat(row['due_date']) < as_of and balance > 0:
            overdue.append({'invoice_id': row['invoice_id'], 'balance': str(balance)})
    print(json.dumps({'as_of_date': str(as_of), 'job_count': len(jobs),
        'included_completed_job_count': sum(r['status']=='completed' for r in jobs)-len(incomplete),
        'revenue': str(revenue), 'direct_cost': str(cost), 'gross_profit': str(revenue-cost),
        'gross_margin_percent': str(((revenue-cost)/revenue*100).quantize(Decimal('0.01'))) if revenue else None,
        'margin_investigations': findings, 'incomplete_jobs': incomplete,
        'overdue_invoices': overdue}, indent=2))

if __name__ == '__main__':
    main()
