import unittest
from unittest.mock import MagicMock, patch
import rules_processing as rp

class TestRulesProcessing(unittest.TestCase):

    def setUp(self):
        self.email = {
            "from": "test@example.com",
            "subject": "Test Subject",
            "body": "Hello world",
            "date": "2025-09-26"
        }
        self.rule_all = {
            "predicate": "All",
            "rules": [
                {"field": "from", "predicate": "contains", "value": "test"},
                {"field": "subject", "predicate": "contains", "value": "Subject"}
            ]
        }
        self.rule_any = {
            "predicate": "Any",
            "rules": [
                {"field": "from", "predicate": "contains", "value": "abc"},
                {"field": "subject", "predicate": "contains", "value": "Subject"}
            ]
        }

    def test_load_rules(self):
        rules = rp.load_rules("rules.json")
        self.assertIsInstance(rules, list)

    def test_evaluate_all(self):
        self.assertTrue(rp.evaluate(self.email, self.rule_all))

    def test_evaluate_any(self):
        self.assertTrue(rp.evaluate(self.email, self.rule_any))

    def test_sanitize_label_name(self):
        name = "New/Label*Name?"
        sanitized = rp.sanitize_label_name(name)
        self.assertEqual(sanitized, "NewLabelName")

    def test_apply_mark_as_read_unread(self):
        service = MagicMock()
        service.users().messages().get().execute.return_value = {"labelIds": ["UNREAD"]}
        rp.apply(service, "msg123", ["mark_as_read", "mark_as_unread"])

        # Check removeLabelIds called for mark_as_read
        service.users().messages().modify.assert_any_call(
            userId="me", id="msg123", body={"removeLabelIds": ["UNREAD"]}
        )
        # Check addLabelIds called for mark_as_unread
        service.users().messages().modify.assert_any_call(
            userId="me", id="msg123", body={"addLabelIds": ["UNREAD"]}
        )

    def test_apply_move_to_creates_label(self):
        service = MagicMock()
        # No existing labels
        service.users().messages().get().execute.return_value = {"labelIds": []}
        service.users().labels().list().execute.return_value = {"labels": []}
        service.users().labels().create().execute.return_value = {"id": "LBL123"}

        rp.apply(service, "msg123", ["move_to:NewLabel"])

        # Check that create was called with correct args
        service.users().labels().create.assert_called_with(
            userId="me",
            body={"name": "NewLabel"}
        )

        # Check modify was called with correct args
        service.users().messages().modify.assert_called_with(
            userId="me",
            id="msg123",
            body={"addLabelIds": ["LBL123"]}
        )

if __name__ == '__main__':
    unittest.main()