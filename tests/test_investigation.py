import json
import unittest
from unittest.mock import patch, MagicMock

from src.data_loader import load_transactions
from src.analysis_service import analyze_transactions
from app import app


class TestTransactionRiskAssistant(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.normal_df = load_transactions("data/normal_case.csv")
        cls.difficult_df = load_transactions("data/transaction.csv")
        cls.app_client = app.test_client()

    def test_normal_case_no_attention_required(self):
        """
        Verify that a routine transaction history is identified as NO ATTENTION REQUIRED
        and produces a plain statement with zero flagged transactions.
        """
        result = analyze_transactions(self.normal_df, include_ai=False)
        report = result["report"]

        self.assertEqual(report["status"], "NO ATTENTION REQUIRED")
        self.assertIn("No significant activity", report["summary"])
        self.assertEqual(len(report["triggered_rules"]), 0)
        self.assertEqual(len(report["flagged_transaction_ids"]), 0)
        self.assertEqual(len(report["findings"]), 0)
        self.assertEqual(report["total_flagged_amount"], 0.0)

    def test_difficult_case_attention_recommended(self):
        """
        Verify that suspicious connected transactions trigger rules,
        flag specific transactions, and recommend investigator attention.
        """
        result = analyze_transactions(self.difficult_df, include_ai=False)
        report = result["report"]

        self.assertEqual(report["status"], "ATTENTION RECOMMENDED")
        self.assertGreater(len(report["triggered_rules"]), 0)
        self.assertEqual(sorted(report["flagged_transaction_ids"]), ["TXN041", "TXN042", "TXN043"])
        self.assertEqual(report["total_flagged_amount"], 160000.00)

        rule_ids = {r["rule_id"] for r in report["triggered_rules"]}
        self.assertIn("RISK-01", rule_ids)
        self.assertIn("RISK-02", rule_ids)
        self.assertIn("RISK-03", rule_ids)
        self.assertIn("RISK-04", rule_ids)

    def test_traceability_to_input_history(self):
        """
        Verify that every transaction cited in findings exists in the input CSV history.
        """
        result = analyze_transactions(self.difficult_df, include_ai=False)
        input_ids = set(self.difficult_df["transaction_id"])

        for finding in result["report"]["findings"]:
            self.assertIn(finding["transaction_id"], input_ids)

    def test_non_accusatory_tone(self):
        """
        Verify that deterministic outputs never assert that fraud has occurred.
        """
        result = analyze_transactions(self.difficult_df, include_ai=False)
        summary = result["report"]["summary"]

        self.assertNotIn("fraud occurred", summary.lower())
        self.assertNotIn("guilty", summary.lower())
        self.assertNotIn("fraudster", summary.lower())

    def test_ai_investigation_integration(self):
        """
        Verify that the Gemini integration converts a grounded
        model response into the expected structured investigation schema.

        The Gemini API is mocked so this test does not depend on
        live API availability, quota, or network conditions.
        """

        fake_response_data = {
            "attention_assessment": (
                "Three verified transactions require investigator review."
            ),
            "key_findings": [
                "TXN041 is a verified flagged transaction.",
                "TXN042 is a verified flagged transaction.",
                "TXN043 is a verified flagged transaction.",
            ],
            "connected_activity": [
                (
                    "TXN041, TXN042 and TXN043 were sent to the same "
                    "payee within a short time window."
                )
            ],
            "deviation_from_normal_behaviour": [
                (
                    "The transaction amounts and timing differ "
                    "from the customer's historical behaviour."
                )
            ],
            "investigator_priority": [
                "Review TXN041 first.",
                "Review the linked transactions and payee relationship.",
            ],
            "limitation": (
                "These indicators do not establish that fraud occurred. "
                "Human investigation is required."
            ),
        }

        mock_response = MagicMock()
        mock_response.text = json.dumps(fake_response_data)

        with patch(
            "src.gemini_service.genai.Client"
        ) as mock_client:

            mock_client.return_value.models.generate_content.return_value = (
                mock_response
            )

            with patch.dict(
                "os.environ",
                {
                    "GEMINI_API_KEY": "test-api-key"
                },
            ):

                result = analyze_transactions(
                    self.difficult_df,
                    include_ai=True,
                )

        ai_resp = result["ai_investigation"]

        self.assertTrue(
            ai_resp["available"]
        )

        self.assertIn(
            "structured",
            ai_resp,
        )

        structured = ai_resp["structured"]

        self.assertTrue(
            structured["attention_assessment"]
        )

        self.assertGreater(
            len(structured["key_findings"]),
            0,
        )

        self.assertGreater(
            len(structured["connected_activity"]),
            0,
        )

        self.assertGreater(
            len(
                structured[
                    "deviation_from_normal_behaviour"
                ]
            ),
            0,
        )

        self.assertGreater(
            len(
                structured[
                    "investigator_priority"
                ]
            ),
            0,
        )

        self.assertIn(
            "do not establish that fraud occurred",
            structured["limitation"].lower(),
        )

    def test_flask_home_route(self):
        """
        Verify that home page loads with 200 OK.
        """
        response = self.app_client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_flask_analyze_normal_route(self):
        """
        Verify POST /analyze for normal case returns 200 OK and NO ATTENTION REQUIRED HTML.
        """
        response = self.app_client.post("/analyze", data={"case_type": "normal"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"NO ATTENTION REQUIRED", response.data)

    def test_flask_analyze_difficult_route(self):
        """
        Verify POST /analyze for difficult case returns 200 OK and ATTENTION RECOMMENDED HTML.
        """
        response = self.app_client.post("/analyze", data={"case_type": "difficult"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"ATTENTION RECOMMENDED", response.data)


if __name__ == "__main__":
    unittest.main()
