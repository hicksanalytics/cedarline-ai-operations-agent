import json
import urllib.error
import urllib.request
from datetime import date

from tools import get_job_margin_report, get_overdue_invoices

MODEL = "qwen3:4b-instruct"
URL = "http://localhost:11434/api/chat"

INSTRUCTIONS = """
You are Cedarline's operations analyst.

For profitability questions, call get_job_margin_report.
For company-wide profitability, use branch_id="All".
For overdue invoices or collections, call get_overdue_invoices.
For questions about both topics, call both tools.

Use the report date supplied by the user.
If an invoice question has no date, use the training date 2026-10-02
and disclose that assumption.

Never invent financial figures or causes.
Money fields are integer cents; divide by 100 to display dollars.
Margin percentages are already percentages.
Cite job and invoice IDs supporting your findings.

Entries under incomplete_jobs are completed jobs with missing
financial values. Identify the missing fields and disclose that
these jobs are excluded from totals until values are supplied.

The 30% threshold triggers individual job investigation.
It is not an approved overall business margin target.
Do not label overall profitability healthy or unhealthy.
Gross margin here includes labor and materials, not overhead.
The tools do not establish causes of low margins.

An invoice is overdue only if its unpaid balance is positive
and its due date is before the report date.
Do not confuse unpaid invoices with overdue invoices.

These tools read synthetic training data.
You cannot modify records, send messages, or approve actions.
Customer contact details are unavailable.
If evidence is insufficient, explain what is missing.
"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_job_margin_report",
            "description": (
                "Get completed-job profitability for the entire "
                "company or one branch. Use All for company-wide "
                "or overall questions. Returns margins, totals, "
                "flagged jobs, and missing financial fields."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "branch_id": {
                        "type": "string",
                        "enum": ["All", "North", "East", "South"],
                    }
                },
                "required": ["branch_id"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_overdue_invoices",
            "description": (
                "Find overdue invoices for collection review. "
                "Returns invoice IDs, balances, and days overdue. "
                "Requires a report date formatted YYYY-MM-DD."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "as_of_date": {
                        "type": "string",
                        "description": "Report date as YYYY-MM-DD.",
                    }
                },
                "required": ["as_of_date"],
                "additionalProperties": False,
            },
        },
    },
]


def ask_model(messages):
    payload = {
        "model": MODEL,
        "messages": messages,
        "tools": TOOLS,
        "stream": False,
        "options": {
            "temperature": 0,
            "num_ctx": 4096,
            "num_predict": 512,
        },
    }

    request = urllib.request.Request(
        URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    opener = urllib.request.build_opener(
        urllib.request.ProxyHandler({})
    )

    with opener.open(request, timeout=300) as response:
        return json.load(response)


def execute_tool(name, arguments):
    if not isinstance(arguments, dict):
        return {"error": "Arguments must be an object."}

    if name == "get_job_margin_report":
        if set(arguments) != {"branch_id"}:
            return {"error": "Expected only branch_id."}

        branch = arguments["branch_id"]
        if branch not in ("All", "North", "East", "South"):
            return {"error": "Invalid branch."}

        return get_job_margin_report(
            None if branch == "All" else branch
        )

    if name == "get_overdue_invoices":
        if set(arguments) != {"as_of_date"}:
            return {"error": "Expected only as_of_date."}

        value = arguments["as_of_date"]
        if not isinstance(value, str):
            return {"error": "Date must be a YYYY-MM-DD string."}

        try:
            parsed = date.fromisoformat(value)
        except ValueError:
            return {"error": "Invalid date. Use YYYY-MM-DD."}

        if parsed.isoformat() != value:
            return {"error": "Use the exact YYYY-MM-DD format."}

        return get_overdue_invoices(value)

    return {"error": "Unknown tool."}


def main():
    question = input("Ask Cedarline: ").strip()
    if not question:
        return

    messages = [
        {"role": "system", "content": INSTRUCTIONS},
        {"role": "user", "content": question},
    ]

    tool_count = 0
    successful_tools = set()
    unresolved_errors = {}
    recovery_used = False
    argument_retry_used = False

    for turn in range(6):
        print(f"\n[Local model request {turn + 1}]")

        response = ask_model(messages)
        message = response.get("message")

        if not isinstance(message, dict):
            raise RuntimeError("Ollama returned no usable message.")

        messages.append(message)
        calls = message.get("tool_calls") or []

        if not calls:
            if unresolved_errors:
                if not argument_retry_used:
                    argument_retry_used = True
                    print(
                        "[Validation check] Retrying failed tool arguments."
                    )
                    messages.append({
                        "role": "user",
                        "content": (
                            "Some tool calls failed validation: "
                            + json.dumps(unresolved_errors)
                            + ". Call those tools again with corrected "
                            "arguments before answering. Read the date "
                            "from my original question and express it "
                            "exactly as YYYY-MM-DD. Original question: "
                            + question
                        ),
                    })
                    continue

                print(
                    "\nIncomplete report: tool errors remain unresolved."
                )
                print(json.dumps(unresolved_errors, indent=2))
                print(
                    "Successful tools: "
                    + ", ".join(sorted(successful_tools))
                )
                return

            if not successful_tools:
                if not recovery_used:
                    recovery_used = True
                    print(
                        "[Evidence check] Allowing one corrective attempt."
                    )
                    messages.append({
                        "role": "user",
                        "content": (
                            "Query the appropriate tools before answering. "
                            "Use get_job_margin_report for profitability "
                            "and get_overdue_invoices for collections. "
                            "Call both if both topics were requested. "
                            "Use All for company-wide profitability. "
                            "Use the date from my original question, "
                            "formatted YYYY-MM-DD. If no invoice date "
                            "was supplied, use 2026-10-02 and disclose "
                            "that assumption."
                        ),
                    })
                    continue

                print("\nNo verified answer: no successful database query.")
                return

            answer = message.get("content", "").strip()
            if not answer:
                raise RuntimeError("The model returned an empty answer.")

            print("\nCEDARLINE ANALYST\n")
            print(answer)
            print(
                "\n[Successful tools] "
                + ", ".join(sorted(successful_tools))
            )

            if recovery_used:
                print("[Trace: required tool-selection recovery.]")
            if argument_retry_used:
                print("[Trace: required argument correction.]")
            return

        for call in calls:
            if tool_count >= 5:
                raise RuntimeError("Tool-call limit reached.")

            tool_count += 1
            function = call.get("function", {})
            name = function.get("name")
            arguments = function.get("arguments", {})

            print(f"[Tool requested] {name}: {arguments}")
            result = execute_tool(name, arguments)

            if "error" in result:
                unresolved_errors[name] = result["error"]
            else:
                successful_tools.add(name)
                unresolved_errors.pop(name, None)

            print("[Tool result]")
            print(json.dumps(result, indent=2))

            messages.append({
                "role": "tool",
                "tool_name": name,
                "content": json.dumps(result),
            })

    raise RuntimeError("Request limit reached without a final answer.")


if __name__ == "__main__":
    try:
        main()
    except urllib.error.HTTPError as error:
        print(f"\nOllama HTTP error {error.code}:")
        print(error.read().decode("utf-8", errors="replace"))
    except urllib.error.URLError as error:
        print(f"\nCannot reach Ollama: {error.reason}")
        print("Make sure the Ollama application is running.")
    except (TimeoutError, RuntimeError) as error:
        print(f"\nAgent stopped: {error}")