import csv
import sqlite3
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATABASE = ROOT / "data" / "cedarline.db"


def to_cents(value):
    """Store money as integer cents; preserve missing values."""
    if value == "":
        return None

    cents = Decimal(value) * 100
    if cents != cents.to_integral_value():
        raise ValueError(f"Amount has fractions of a cent: {value}")

    return int(cents)


def main():
    with (ROOT / "data" / "jobs.csv").open(newline="") as file:
        jobs = list(csv.DictReader(file))

    connection = sqlite3.connect(DATABASE)

    try:
        with connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    job_id TEXT PRIMARY KEY,
                    branch_id TEXT NOT NULL,
                    service_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    revenue_cents INTEGER,
                    labor_cost_cents INTEGER,
                    material_cost_cents INTEGER
                )
            """)

            # Reload this training table from the CSV.
            connection.execute("DELETE FROM jobs")

            connection.executemany("""
                INSERT INTO jobs VALUES (?, ?, ?, ?, ?, ?, ?)
            """, [
                (
                    job["job_id"],
                    job["branch_id"],
                    job["service_type"],
                    job["status"],
                    to_cents(job["revenue"]),
                    to_cents(job["labor_cost"]),
                    to_cents(job["material_cost"]),
                )
                for job in jobs
            ])

        count = connection.execute(
            "SELECT COUNT(*) FROM jobs"
        ).fetchone()[0]

        missing = connection.execute("""
            SELECT job_id
            FROM jobs
            WHERE labor_cost_cents IS NULL
        """).fetchall()

        print(f"Loaded {count} jobs")
        print(f"Jobs missing labor cost: {[row[0] for row in missing]}")
        print(f"Database: {DATABASE}")

    finally:
        connection.close()


if __name__ == "__main__":
    main()