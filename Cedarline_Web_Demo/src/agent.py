import json
import os

from google import genai
from google.genai import types

from tools import get_job_margin_report


INSTRUCTIONS = """
You are Cedarline's operations analyst.

Use the profitability tool for questions about actual job finances.
Never invent financial numbers or causes of low margins.
Tool monetary values are integer cents: divide by 100 to show dollars.
Margin percentages are already percentages.
Cite job IDs when discussing flagged jobs.
Disclose incomplete jobs and that totals exclude their unknown costs.
Distinguish branch overall margin from individual job margin.
The data is a training snapshot, not a historical or live report.
You cannot send messages, change records, or approve actions.
If the tool cannot answer a question, explain the limitation.
"""


def main():
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise SystemExit("Set GEMINI_API_KEY in this terminal first.")

    question = input("Ask Cedarline: ").strip()
    if not question:
        raise SystemExit("Please enter a question.")

    declaration = types.FunctionDeclaration(
        name="get_job_margin_report",
        description=(
            "Get completed-job profitability and low-margin exceptions. "
            "Branch must be All, North, East, or South."
        ),
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "branch_id": types.Schema(
                    type=types.Type.STRING,
                    enum=["All", "North", "East", "South"],
                )
            },
            required=["branch_id"],
        ),
    )

    config = types.GenerateContentConfig(
        system_instruction=INSTRUCTIONS,
        tools=[types.Tool(function_declarations=[declaration])],
        automatic_function_calling=types.AutomaticFunctionCallingConfig(
            disable=True
        ),
        temperature=0,
    )

    history = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=question)],
        )
    ]

    tool_count = 0

    with genai.Client(api_key=key) as client:
        # Limit this run to six model requests and five tool calls.
        for turn in range(6):
            print(f"\n[Model request {turn + 1}]")

            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=history,
                config=config,
            )

            if not response.candidates:
                raise RuntimeError("Gemini returned no answer candidate.")

            content = response.candidates[0].content
            if not content or not content.parts:
                raise RuntimeError("Gemini returned no usable content.")

            # Preserve the complete model response for the next request.
            history.append(content)

            calls = [
                part.function_call
                for part in content.parts
                if part.function_call is not None
            ]

            if not calls:
                answer = "\n".join(
                    part.text
                    for part in content.parts
                    if part.text and not part.thought
                )
                if not answer:
                    raise RuntimeError("Gemini returned no final answer.")

                print("\nCEDARLINE ANALYST\n")
                print(answer)
                return

            results = []

            for call in calls:
                if tool_count >= 5:
                    raise RuntimeError("Tool-call limit reached.")

                tool_count += 1
                arguments = dict(call.args or {})

                print(f"[Tool requested] {call.name}: {arguments}")

                if call.name != "get_job_margin_report":
                    result = {"error": "Unknown tool."}
                elif set(arguments) != {"branch_id"}:
                    result = {"error": "Expected only branch_id."}
                elif arguments["branch_id"] not in (
                    "All", "North", "East", "South"
                ):
                    result = {"error": "Invalid branch."}
                else:
                    branch = arguments["branch_id"]
                    result = get_job_margin_report(
                        None if branch == "All" else branch
                    )

                print("[Tool result]")
                print(json.dumps(result, indent=2))

                results.append(
                    types.Part.from_function_response(
                        name=call.name,
                        response=result,
                    )
                )

            history.append(
                types.Content(role="tool", parts=results)
            )

    raise RuntimeError("Model-request limit reached without a final answer.")


if __name__ == "__main__":
    main()