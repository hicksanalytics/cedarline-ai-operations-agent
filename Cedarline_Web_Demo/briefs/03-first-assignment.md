# Your first assignment

From Morgan Ellis to Ben Hicks

Please send me a short discovery note before writing the agent. We have heard that our East branch has a margin problem, but I need you to validate that from the records. Tell me which completed jobs deserve investigation, which records are incomplete, and which invoice is overdue as of October 2, 2026. Then recommend what the first agent should be allowed to do.

## Step 1 Understand the inputs

Open the jobs and invoices CSVs and the three policy sections. Identify each table's grain, primary key, foreign key, and missing fields. Explain why joining jobs to multiple invoices can duplicate revenue. Do not assume a single invoice per job just because this sample mostly has one.

## Step 2 Run the baseline

Run `python src/inspect_data.py`. Read its code. Explain why it excludes J104 and J106 from completed-job margin totals and why J105 is reported separately. Recalculate J102's profit and margin yourself.

## Step 3 Submit your discovery note

Use this structure: business problem; three questions for Morgan; definitions and assumptions; findings with evidence IDs; first agent tools and permissions; biggest implementation risk; proposed next step. Keep it under 500 words.

## Step 4 Discuss with your mentor

Bring the output and your note into this conversation. We will review the business logic, then implement the SQLite loader and first read tool together. If you need help installing Python or using VS Code, say which environment you have; setup is the first guided task.

## Reviewer reference

J101: profit $900, margin 75%. J102: profit $100, margin 25%. J103: profit $2,500, margin approximately 36.23%. Totals: revenue $8,500, cost $5,000, profit $3,500, margin approximately 41.18%. J105 is completed but has unknown labor cost; exclude it from the numeric total and disclose it. J104 is canceled. J106 is scheduled. I201 is overdue, with $400 remaining. I203 is unpaid but not overdue on October 2. I204 is paid. The dataset supports investigation of J102, not a general conclusion about the East branch.
