# tests/test_integration.py
import unittest
from unittest.mock import patch, MagicMock
from db_utils import init_db, store_emails
from rules_processing import evaluate
import main  # import main so we can call main.apply

class TestIntegrationMySQL(unittest.TestCase):
    def setUp(self):
        # Use a test database
        self.conn, self.cursor = init_db()
        self.cursor.execute("DROP TABLE IF EXISTS email_inbox")  # ensure clean slate
        self.conn.commit()
        self.conn, self.cursor = init_db()

        # Sample emails
        self.emails = [
            {"id": "1", "from": "a@example.com", "subject": "Hello", "body": "Test body", "date": "2025-09-26"},
            {"id": "2", "from": "b@example.com", "subject": "Interview Invite", "body": "Interview details", "date": "2025-09-25"}
        ]

        # Sample rules
        self.rules = [
            {
                "predicate": "Any",
                "rules": [{"field": "subject", "predicate": "contains", "value": "Interview"}],
                "actions": ["mark_as_read"]
            }
        ]

    @patch("main.authenticate_gmail")
    @patch("main.fetch_emails")
    @patch("main.apply")  # patch main.apply
    def test_main_flow_mysql(self, mock_apply, mock_fetch, mock_auth):
        mock_service = MagicMock()
        mock_auth.return_value = mock_service
        mock_fetch.return_value = self.emails

        # Store emails in MySQL
        store_emails(self.cursor, self.conn, self.emails)

        # Fetch emails from DB
        self.cursor.execute("SELECT email_id, from_user as `from`, subject, body, date_sent as `date` FROM email_inbox")
        db_emails = [dict(zip([c[0] for c in self.cursor.description], row)) for row in self.cursor.fetchall()]

        # Apply rules
        for e in db_emails:
            for rset in self.rules:
                if evaluate(e, rset):
                    # Call the mocked apply from main
                    main.apply(mock_service, e["email_id"], rset["actions"])

        # Assertions
        self.assertEqual(len(db_emails), 2)
        mock_apply.assert_called_once_with(mock_service, "2", ["mark_as_read"])

    def tearDown(self):
        self.cursor.execute("DROP TABLE IF EXISTS email_inbox")
        self.conn.close()

if __name__ == "__main__":
    unittest.main()