import csv
import sqlite3
from datetime import date

from build_database import DATABASE, ROOT, to_cents


def main():
    if not DATABASE.is_file():
        raise FileNotFoundError("Run build_database.py first.")

    with (ROOT / "data" / "invoices.csv").open(newline="") as file:
        invoices = list(csv.DictReader(file))

    records = []

    for invoice in invoices:
        # Validate the date before loading any records.
        due_date = date.fromisoformat(invoice["due_date"])

        amount = to_cents(invoice["amount"])
        paid = to_cents(invoice["paid_amount"])

        if amount is None or paid is None:
            raise ValueError("Invoice amounts must not be missing.")

        if amount < 0 or paid < 0 or paid > amount:
            raise ValueError(
                f"Invalid amounts for {invoice['invoice_id']}"
            )

        records.append((
            invoice["invoice_id"],
            invoice["job_id"],
            due_date.isoformat(),
            amount,
            paid,
        ))

    connection = sqlite3.connect(DATABASE)

    try:
        connection.execute("PRAGMA foreign_keys = ON")

        with connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS invoices (
                    invoice_id TEXT PRIMARY KEY,
                    job_id TEXT NOT NULL REFERENCES jobs(job_id),
                    due_date TEXT NOT NULL,
                    amount_cents INTEGER NOT NULL,
                    paid_amount_cents INTEGER NOT NULL
                )
            """)

            # Reload the training invoices from the CSV.
            connection.execute("DELETE FROM invoices")

            connection.executemany("""
                INSERT INTO invoices VALUES (?, ?, ?, ?, ?)
            """, records)

        count = connection.execute(
            "SELECT COUNT(*) FROM invoices"
        ).fetchone()[0]

        print(f"Loaded {count} invoices")

    finally:
        connection.close()


if __name__ == "__main__":
    main()