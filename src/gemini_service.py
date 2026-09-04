import time
import json
import os

from google import genai


def generate_ai_investigation(report):
    """
    Generate an investigator-facing explanation using only
    verified findings from the deterministic risk engine.

    Gemini does not determine whether fraud occurred and must
    not invent transactions or evidence.
    """

    api_key = os.getenv("GEMINI_API_KEY")

    # Graceful fallback when API key is unavailable
    if not api_key:
        return {
            "available": False,
            "content": (
                "AI investigation narrative is unavailable because "
                "GEMINI_API_KEY is not configured. "
                "Deterministic investigation results remain available."
            ),
        }

    # No need to call Gemini when nothing needs attention
    if report["status"] == "NO ATTENTION REQUIRED":
        return {
            "available": True,
            "content": (
                "No significant activity requiring review was identified. "
                "The transaction history appears consistent with the "
                "customer's established behaviour."
            ),
        }

    verified_report = json.dumps(
        report,
        indent=2,
        ensure_ascii=False,
    )

    prompt = f"""
You are an AI assistant supporting a banking transaction investigator.

Your role is to EXPLAIN verified risk findings.
You are NOT a fraud detection system and you must NOT determine
that fraud has occurred.

STRICT RULES:

1. Use ONLY the evidence contained in VERIFIED INVESTIGATION DATA.
2. Never invent transaction IDs, amounts, payees, dates, times,
   channels, risk rules, or customer behaviour.
3. Never state or imply that fraud definitely occurred.
4. Use cautious language such as:
   "requires review",
   "unusual activity",
   "deviates from historical behaviour",
   or "warrants further investigation".
5. Clearly explain how the flagged transactions connect.
6. Explain how the activity differs from the customer's normal behaviour.
7. Tell the investigator what should be examined first.
8. If evidence is insufficient for a conclusion, say so.
9. Every transaction you mention must exist in the verified data.
10. Keep the response concise and professional.

Return the report using exactly these sections:

ATTENTION ASSESSMENT
State whether the activity requires investigator attention.

KEY FINDINGS
Explain the important verified findings.

CONNECTED ACTIVITY
Explain how the flagged transactions relate to each other.

DEVIATION FROM NORMAL BEHAVIOUR
Explain how the activity differs from established behaviour.

INVESTIGATOR PRIORITY
Explain what the human investigator should examine first.

LIMITATION
State clearly that these indicators do not establish that fraud occurred
and require human review.

FORMATTING REQUIREMENTS:

- Return clean Markdown only.
- Use ### for each required section heading.
- Use standard Markdown bullet points using "- ".
- Use numbered lists only for investigator priorities.
- Do not escape Markdown characters.
- Do not use HTML.
- Do not use Markdown tables.
- Do not wrap the response in a code block.
- Keep transaction IDs and important values in bold where useful.

VERIFIED INVESTIGATION DATA:

{verified_report}
"""

    try:
        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model="gemini-3.7-flash",
            contents=prompt,
    
        )

        if not response.text:
            raise ValueError("Gemini returned an empty response.")

        return {
        "available": True,
        "content": response.text.strip(),
    }

    except Exception as error:
        return {
        "available": False,
        "content": (
            "AI investigation narrative could not be generated. "
            "Deterministic investigation results remain available. "
            f"Reason: {error}"
        ),
    }