import os
import unittest
import pandas as pd
from flask import Flask

from src.data_loader import load_transactions
from src.analysis_service import analyze_transactions
from src.risk_engine import (
    detect_large_transfers,
    detect_new_payee_bursts,
    detect_odd_hours,
    detect_behavior_deviation,
)
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
        Verify that AI investigation generates expected sections when API key is provided.
        """
        if not os.getenv("GEMINI_API_KEY"):
            self.skipTest("GEMINI_API_KEY not configured")

        result = analyze_transactions(self.difficult_df, include_ai=True)
        ai_resp = result["ai_investigation"]
        self.assertTrue(ai_resp["available"])
        content = ai_resp["content"]
        self.assertIn("ATTENTION ASSESSMENT", content)
        self.assertIn("KEY FINDINGS", content)
        self.assertIn("CONNECTED ACTIVITY", content)
        self.assertIn("DEVIATION FROM NORMAL BEHAVIOUR", content)
        self.assertIn("INVESTIGATOR PRIORITY", content)
        self.assertIn("LIMITATION", content)
        self.assertNotIn("fraud has occurred", content.lower())

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
