from __future__ import print_function
import os.path
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
import html2text  

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def authenticate_gmail():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def get_body_from_payload(payload):
    """Extract email body, fallback to HTML if plain text is missing"""
    body = ''
    parts = payload.get('parts')
    if parts:
        # First try text/plain
        for part in parts:
            if part.get('mimeType') == 'text/plain' and part.get('body', {}).get('data'):
                body = base64.urlsafe_b64decode(part['body']['data'].encode('ASCII')).decode('utf-8')
                break
        # Fallback to HTML
        if not body:
            for part in parts:
                if part.get('mimeType') == 'text/html' and part.get('body', {}).get('data'):
                    html_body = base64.urlsafe_b64decode(part['body']['data'].encode('ASCII')).decode('utf-8')
                    body = html2text.html2text(html_body)
                    break
    else:
        # Single-part email
        if payload.get('body', {}).get('data'):
            body = base64.urlsafe_b64decode(payload['body']['data'].encode('ASCII')).decode('utf-8')
    return body.strip()

def fetch_emails(service, max_results=10):
    try:
        results = service.users().messages().list(
            userId='me', maxResults=max_results, q='in:inbox'
        ).execute()
        messages = results.get('messages', [])
        emails = []

        for msg in messages:
            msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
            payload = msg_data['payload']
            headers = payload['headers']

            email_dict = {
                'id': msg['id'],
                'thread_id': msg_data['threadId'],
                'from': '',
                'subject': '',
                'date': '',
                'body': ''
            }

            for header in headers:
                if header['name'] == 'From':
                    email_dict['from'] = header['value']
                elif header['name'] == 'Subject':
                    email_dict['subject'] = header['value']
                elif header['name'] == 'Date':
                    email_dict['date'] = header['value']

            email_dict['body'] = get_body_from_payload(payload)
            emails.append(email_dict)

        return emails

    except HttpError as error:
        print(f'An error occurred: {error}')
        return []

if __name__ == '__main__':
    service = authenticate_gmail()
    emails = fetch_emails(service, max_results=5)
    for e in emails:
        body_preview = e.get('body', '')[:200].replace('\n', ' ')
        print(f"From: {e.get('from')}, Subject: {e.get('subject')}, Date: {e.get('date')}, Body Preview: {body_preview}\n")