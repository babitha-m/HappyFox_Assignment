from __future__ import print_function
import os.path
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request


# If modifying these scopes, delete the file token.json
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def authenticate_gmail():
    creds = None
    # token.json stores the user's access and refresh tokens
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If no valid credentials, start OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save credentials for next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def fetch_emails(service, max_results=10):
    try:
        # Fetch list of messages
        results = service.users().messages().list(userId='me', maxResults=max_results, q='in:inbox').execute()  #Fetch from only inbox
        messages = results.get('messages', [])
        emails = []

        for msg in messages:
            msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
            payload = msg_data['payload']
            headers = payload['headers']

            email_dict = {'id': msg['id'], 'thread_id': msg_data['threadId']}
            for header in headers:
                if header['name'] == 'From':
                    email_dict['from'] = header['value']
                if header['name'] == 'Subject':
                    email_dict['subject'] = header['value']
                if header['name'] == 'Date':
                    email_dict['date'] = header['value']

            # Get email body (plain text)
            parts = payload.get('parts')
            body = ''
            if parts:
                for part in parts:
                    if part['mimeType'] == 'text/plain':
                        body = base64.urlsafe_b64decode(part['body']['data'].encode('ASCII')).decode('utf-8')
            else:
                body = base64.urlsafe_b64decode(payload['body']['data'].encode('ASCII')).decode('utf-8')

            email_dict['body'] = body
            emails.append(email_dict)

        return emails

    except HttpError as error:
        print(f'An error occurred: {error}')
        return []

if __name__ == '__main__':
    service = authenticate_gmail()
    emails = fetch_emails(service, max_results=10)
    for e in emails:
        print(f"From: {e['from']}, Subject: {e['subject']}, Date: {e['date']}, Body: {e['body']}\n")