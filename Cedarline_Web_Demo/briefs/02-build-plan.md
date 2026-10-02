# Build plan and acceptance gates

## Proposed stack

Python for business logic and tools; SQLite for the initial operational database; one tool-capable LLM provider added later; local document retrieval; a small web interface after the workflow works. We will check current official documentation when choosing the model API and orchestration library. Begin with an explicit state machine rather than adding a framework before you need it. Local deterministic work is free; hosted model calls may cost money. Model access is not included with this packet.

## Milestone 1 Data foundation

Load the CSVs into SQLite. Define keys and joins, validate numeric types, retain nulls, and implement `get_job_margin_report(as_of_date, branch_id)` and `get_overdue_invoices(as_of_date)`. Return structured records with evidence IDs and warnings. Demonstrate that duplicate joins do not inflate revenue and that missing costs remain excluded and visible. Add cases for zero revenue, duplicate IDs, invalid dates, and partial payment.

## Milestone 2 One tool using agent

Build an agent that receives a manager's question, chooses from the two tools, observes results, and writes an evidence-backed answer. Distinguish this from a fixed script: the model chooses a permitted tool and arguments based on the question. Validate arguments outside the model. Enforce branch scope server-side. Cap a run at five tool calls and two retries; stop with a clear error when the budget is exhausted. No arbitrary SQL execution tool. Start with an allowlist of parameterized queries.

Demo: Ask which completed jobs need margin investigation and which invoices need collection review. Unknown customers and missing costs must trigger explicit uncertainty.

## Milestone 3 Policy retrieval

Index the supplied documents with document ID, section, effective date, and revision. Implement `search_policy(query)` and preserve source passages. Begin with simple text retrieval and measure its limitations before adding embeddings. Answer policy questions with citations. Business data calculations still come from tools. Add an outdated document and a document containing hostile instructions to prove that document content cannot change permissions.

## Milestone 4 Coordinated investigation

Route financial analysis to the analyst and policy questions to the policy agent. Use shared typed state with request ID, role, branch scope, as-of date, evidence, warnings, and proposed actions. Persist state between steps. Do not send the entire history to every agent. Track tool traces, latency, model usage, and run outcome. Show where deterministic checks are stronger than another agent.

## Milestone 5 Approved actions

Implement `propose_task`, `approve_action`, and `execute_approved_action` as separate operations in a simulated task store. Approval binds to the exact proposal payload and expires after 24 hours. A changed payload needs new approval. The backend verifies the approving role; the model cannot approve. A unique idempotency key prevents duplicate task creation. Persist execution status and handle a crash after execution before acknowledgment by checking the stored key before retrying.

Demo: Propose an internal review for J102. A manager reviews the evidence, approves it, and creates exactly one simulated task. Test rejection, expiry, tampering, unauthorized approval, and retry.

## Milestone 6 Evaluation and client demonstration

Expand the initial evaluation cases to at least 30, including paraphrases, insufficient evidence, role restrictions, and tool failures. Score numeric correctness separately from prose quality. Target 100% financial fixture correctness, zero unauthorized executions across the test suite, and at least 90% correct policy citations on the labeled set. These are pilot gates, not guarantees outside the test set. Record failed cases rather than quietly changing expectations.

Deliver a reproducible setup, architecture explanation, evaluation report, sample traces, and five-minute recorded or live demo. Compare manual baseline time against assisted workflow time; do not claim business ROI without measured evidence.

## Stretch work after the pilot

Add event-triggered daily exception reports, competing technician availability constraints, tenant isolation, a second synthetic client, queue-based execution, or a model/provider comparison. Select one after the core gates pass. More agents are not automatically better.

## Output contract

Every investigation returns: `request_id`, `as_of_date`, `summary`, `findings`, `evidence`, `warnings`, `proposed_actions`, and `status`. Each finding identifies its supporting records or policy sections. A suggested cause is labeled a hypothesis unless records prove it.
