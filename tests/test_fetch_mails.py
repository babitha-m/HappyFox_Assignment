# tests/test_fetch_mails.py
import unittest
from unittest.mock import MagicMock, patch
import base64
import fetch_mails


class TestFetchMails(unittest.TestCase):

    def test_get_body_from_payload_plain_text(self):
        payload = {
            "parts": [
                {"mimeType": "text/plain", "body": {"data": base64.urlsafe_b64encode(b"Hello World").decode("ascii")}}
            ]
        }
        body = fetch_mails.get_body_from_payload(payload)
        self.assertEqual(body, "Hello World")

    def test_get_body_from_payload_html(self):
        html = "<p>Hello <b>World</b></p>"
        payload = {
            "parts": [
                {"mimeType": "text/html", "body": {"data": base64.urlsafe_b64encode(html.encode()).decode("ascii")}}
            ]
        }
        body = fetch_mails.get_body_from_payload(payload)
        self.assertIn("Hello", body)

    def test_get_body_from_payload_single_part(self):
        payload = {
            "body": {"data": base64.urlsafe_b64encode(b"Single Part Body").decode("ascii")}
        }
        body = fetch_mails.get_body_from_payload(payload)
        self.assertEqual(body, "Single Part Body")

    @patch("fetch_mails.build")
    def test_fetch_emails(self, mock_build):
        # Mock Gmail service
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Mock list() -> execute() to return one message
        mock_service.users().messages().list().execute.return_value = {
            "messages": [{"id": "123"}]
        }

        # Mock get() -> execute() to return email data
        mock_service.users().messages().get().execute.return_value = {
            "id": "123",
            "threadId": "t1",
            "payload": {
                "headers": [
                    {"name": "From", "value": "test@example.com"},
                    {"name": "Subject", "value": "Test Subject"},
                    {"name": "Date", "value": "2025-09-26"}
                ],
                "body": {"data": base64.urlsafe_b64encode(b"Test Body").decode("ascii")}
            }
        }

        emails = fetch_mails.fetch_emails(mock_service, max_results=1)
        self.assertEqual(len(emails), 1)
        self.assertEqual(emails[0]["id"], "123")
        self.assertEqual(emails[0]["from"], "test@example.com")
        self.assertEqual(emails[0]["subject"], "Test Subject")
        self.assertEqual(emails[0]["date"], "2025-09-26")
        self.assertEqual(emails[0]["body"], "Test Body")


if __name__ == "__main__":
    unittest.main()
