import json
import os

from google import genai


def _fallback_response(message):
    """
    Return a consistent fallback schema so the UI and PDF
    can render safely even when Gemini is unavailable.
    """
    return {
        "available": False,
        "content": message,
        "structured": {
            "attention_assessment": message,
            "key_findings": [],
            "connected_activity": [],
            "deviation_from_normal_behaviour": [],
            "investigator_priority": [],
            "limitation": (
                "Deterministic investigation results remain available. "
                "Final judgment remains with the human investigator."
            ),
        },
    }


def _validate_string_list(value):
    """
    Ensure Gemini list fields are safe lists of strings.
    """
    if not isinstance(value, list):
        return []

    cleaned = []

    for item in value:
        if isinstance(item, str) and item.strip():
            cleaned.append(item.strip())

    return cleaned


def _build_structured_response(data):
    """
    Normalize Gemini JSON into the schema expected by
    the dashboard and PDF generator.
    """

    attention_assessment = data.get(
        "attention_assessment",
        "",
    )

    limitation = data.get(
        "limitation",
        "",
    )

    if not isinstance(attention_assessment, str):
        attention_assessment = ""

    if not isinstance(limitation, str):
        limitation = ""

    return {
        "attention_assessment": attention_assessment.strip(),
        "key_findings": _validate_string_list(
            data.get("key_findings", [])
        ),
        "connected_activity": _validate_string_list(
            data.get("connected_activity", [])
        ),
        "deviation_from_normal_behaviour": (
            _validate_string_list(
                data.get(
                    "deviation_from_normal_behaviour",
                    [],
                )
            )
        ),
        "investigator_priority": _validate_string_list(
            data.get(
                "investigator_priority",
                [],
            )
        ),
        "limitation": limitation.strip(),
    }


def generate_ai_investigation(report):
    """
    Generate a structured investigator-facing explanation using
    only verified findings from the deterministic risk engine.

    Gemini does not determine whether fraud occurred and must
    not invent transactions or evidence.
    """

    api_key = os.getenv("GEMINI_API_KEY")

    # ---------------------------------------------------------
    # API KEY FALLBACK
    # ---------------------------------------------------------

    if not api_key:
        return _fallback_response(
            "AI investigation narrative is unavailable because "
            "GEMINI_API_KEY is not configured."
        )

    # ---------------------------------------------------------
    # NORMAL CASE
    # ---------------------------------------------------------

    if report["status"] == "NO ATTENTION REQUIRED":

        structured = {
            "attention_assessment": (
                "No significant activity requiring review was identified."
            ),
            "key_findings": [
                (
                    "The supplied transaction history appears "
                    "consistent with the customer's established behaviour."
                )
            ],
            "connected_activity": [],
            "deviation_from_normal_behaviour": [],
            "investigator_priority": [],
            "limitation": (
                "No unusual activity requiring investigation was identified. "
                "Final judgment remains with the human investigator."
            ),
        }

        return {
            "available": True,
            "content": structured["attention_assessment"],
            "structured": structured,
        }

    # ---------------------------------------------------------
    # VERIFIED DETERMINISTIC DATA
    # ---------------------------------------------------------

    verified_report = json.dumps(
        report,
        indent=2,
        ensure_ascii=False,
    )

    # ---------------------------------------------------------
    # GEMINI PROMPT
    # ---------------------------------------------------------

    prompt = f"""
You are an AI assistant supporting a banking transaction investigator.

Your role is ONLY to explain verified deterministic risk findings.

You are NOT a fraud detection system.
You must NOT determine that fraud occurred.

STRICT GROUNDING RULES:

1. Use ONLY evidence contained in VERIFIED INVESTIGATION DATA.
2. Never invent:
   - transaction IDs
   - amounts
   - payees
   - dates
   - times
   - channels
   - risk rules
   - customer behaviour
3. Never claim or imply that fraud definitely occurred.
4. Use cautious investigator-facing language such as:
   - "requires review"
   - "unusual activity"
   - "deviates from historical behaviour"
   - "warrants further investigation"
5. Every transaction mentioned must exist in the verified data.
6. Explain how flagged transactions connect.
7. Explain how activity differs from historical behaviour.
8. Prioritize what the investigator should examine first.
9. Do not invent bank policies or procedures that are not in the data.
10. If evidence is insufficient, say so clearly.
11. Keep the response concise and professional.

RETURN ONLY VALID JSON.

Do not return Markdown.
Do not return HTML.
Do not wrap the JSON in a code block.
Do not include any text before or after the JSON.

Use exactly this JSON structure:

{{
  "attention_assessment": "string",
  "key_findings": [
    "string"
  ],
  "connected_activity": [
    "string"
  ],
  "deviation_from_normal_behaviour": [
    "string"
  ],
  "investigator_priority": [
    "string"
  ],
  "limitation": "string"
}}

FIELD REQUIREMENTS:

attention_assessment:
- Clearly state whether the activity requires investigator attention.
- Mention the number of flagged transactions and total flagged amount
  only if present in verified data.

key_findings:
- Each item must describe one important verified finding.
- Mention exact transaction IDs only when present in verified data.

connected_activity:
- Explain verified relationships such as:
  same payee,
  same channel,
  rapid timing,
  shared transaction pattern.

deviation_from_normal_behaviour:
- Explain verified differences from historical behaviour.
- Use only values present in the deterministic report.

investigator_priority:
- Return an ordered list of what should be examined first.
- Keep priorities grounded in the verified transaction evidence.
- Do not invent internal bank procedures, policies, or records.

limitation:
- Clearly state that risk indicators do not establish that fraud occurred.
- State that human investigation is required.

VERIFIED INVESTIGATION DATA:

{verified_report}
"""

    try:

        client = genai.Client(
            api_key=api_key
        )

        response = client.models.generate_content(
            model="gemini-3.7-flash",
            contents=prompt,
        )

        if not response.text:
            raise ValueError(
                "Gemini returned an empty response."
            )

        raw_text = response.text.strip()

        # -----------------------------------------------------
        # REMOVE CODE FENCES IF MODEL RETURNS THEM ANYWAY
        # -----------------------------------------------------

        if raw_text.startswith("```"):

            raw_text = raw_text.strip("`")

            if raw_text.startswith("json"):
                raw_text = raw_text[4:].strip()

        # -----------------------------------------------------
        # PARSE JSON
        # -----------------------------------------------------

        data = json.loads(
            raw_text
        )

        structured = _build_structured_response(
            data
        )

        # -----------------------------------------------------
        # REQUIRED FIELD VALIDATION
        # -----------------------------------------------------

        if not structured["attention_assessment"]:
            raise ValueError(
                "Gemini response is missing attention_assessment."
            )

        if not structured["limitation"]:
            raise ValueError(
                "Gemini response is missing limitation."
            )

        return {
            "available": True,
            "content": structured["attention_assessment"],
            "structured": structured,
        }

    except json.JSONDecodeError:

        return _fallback_response(
            "AI investigation narrative could not be structured "
            "because Gemini returned an invalid response."
        )

    except Exception as error:

        error_text = str(error)

        if (
            "429" in error_text
            or "RESOURCE_EXHAUSTED" in error_text
        ):
            message = (
                "AI investigation narrative is temporarily unavailable "
                "because the Gemini API quota was reached."
            )

        elif (
            "503" in error_text
            or "UNAVAILABLE" in error_text
        ):
            message = (
                "AI investigation narrative is temporarily unavailable."
            )

        else:
            message = (
                "AI investigation narrative could not be generated."
            )

        return _fallback_response(
            message
        )