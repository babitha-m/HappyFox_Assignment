# tests/test_db_utils.py
import unittest
from unittest.mock import patch, MagicMock
import db_utils

class TestDBUtilsMock(unittest.TestCase):

    @patch('db_utils.mysql.connector.connect')
    def test_init_db(self, mock_connect):
        # Mock connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        conn, cursor = db_utils.init_db()

        # Check if connection and cursor are returned
        self.assertEqual(conn, mock_conn)
        self.assertEqual(cursor, mock_cursor)

        # Check if CREATE TABLE query was executed
        mock_cursor.execute.assert_called()
        mock_conn.commit.assert_called()

    @patch('db_utils.mysql.connector.connect')
    def test_store_emails(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        emails = [
            {
                "id": "1",
                "from": "recruiter@happyfox.com",
                "subject": "Job Opportunity at HappyFox",
                "body": "Details about the job opening",
                "date": "2025-09-26",
                "Received": "2025-09-26"
            },
            {
                "id": "2",
                "from": "admin@pesu.edu",
                "subject": "Exam Schedule",
                "body": "Schedule for upcoming exams",
                "date": "2025-09-25",
                "Received": "2025-09-25"
            },
            {
                "id": "3",
                "from": "hr@linkedin.com",
                "subject": "Interview Invitation",
                "body": "Interview details enclosed",
                "date": "2025-09-24",
                "Received": "2025-09-24"
            }
        ]

        conn, cursor = db_utils.init_db()
        db_utils.store_emails(cursor, conn, emails)

        # Check if INSERT was called with correct parameters
        mock_cursor.execute.assert_called_with(
            """
                INSERT INTO email_inbox (email_id, from_user, subject, body, date_sent)
                VALUES (%s, %s, %s, %s, %s)
            """,
            ("3", "hr@linkedin.com", "Interview Invitation", "Interview details enclosed", "2025-09-24")
        )
        mock_conn.commit.assert_called()

        
if __name__ == '__main__':
    unittest.main()