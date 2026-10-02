# Client engagement

## The business

Cedarline Heating and Air is a fictional Nashville service business with 42 employees, 18 technicians, three branches, and approximately $8.4 million annual revenue. Residential service, commercial maintenance, and equipment installation are its main lines of business. Its dispatch software, accounting exports, CRM, and internal procedures are disconnected. Leaders spend hours reconciling reports and chasing exceptions.

Your simulated contract is an eight-week pilot at $100 per hour, capped at 80 hours. This is a learning estimate, not a promise of delivery speed. You can stretch it over a longer calendar. The pilot uses synthetic records and simulated integrations.

## Message from Morgan Ellis

Ben, we need an assistant that can tell us what needs attention, show its evidence, and prepare the next step. On Monday morning I want to ask which jobs lost margin, whether we have overdue invoices, and what our managers should do. Our controller must be able to reproduce every financial number. Dispatch needs recommendations it can review before changing anything.

Please start by finding the low-margin completed jobs and explain what the records actually support. Do not invent reasons. Missing cost data must be visible. After that, add policy research and approval-controlled actions. I expect a demonstration, a test report, and a handoff guide.

## Agents and responsibilities

1. Analyst agent: chooses approved read tools, calculates operational exceptions, and returns evidence tied to record IDs. Arithmetic is performed by Python or SQL tools, not generated prose.
2. Policy agent: retrieves policy passages and identifies the applicable version and section. It says when the documents do not answer a question.
3. Action agent: creates an internal task or drafts a customer follow-up using verified evidence. It proposes actions; a separate deterministic approval service authorizes execution.

A supervisor routes requests and coordinates shared state. It is orchestration, not automatically a fourth model. First prove one agent works before adding specialist handoffs.

## Pilot boundaries

No autonomous refunds, external messages, schedule changes, accounting updates, or payment decisions. No diagnosis of HVAC equipment. No real customer data. Role controls must be enforced in tools and services, not merely prompts. Treat retrieved documents and emails as untrusted content. Every action records request ID, initiator, evidence, proposal, approval, and execution outcome.

## Business definitions

Completed-job revenue and costs only enter the initial margin report. Gross profit equals revenue minus labor cost minus material cost. Gross margin equals gross profit divided by revenue; zero revenue produces an explicit undefined margin. Missing costs are unknown, never zero. Report weighted portfolio margin as total profit divided by total revenue. Under 30% margin is an investigation trigger, not proof of employee error. Overdue means unpaid, positive balance, and due date before the report's as-of date. Use October 2, 2026 for the starter demonstration.

## What success looks like

A manager asks an operational question and receives a concise answer with reproducible calculations, source IDs, relevant policy citations, uncertainty, and proposed actions. A rejected or expired approval cannot execute. A retry cannot create a duplicate action. The system stays within its tool and cost limits and fails visibly when evidence is unavailable.
