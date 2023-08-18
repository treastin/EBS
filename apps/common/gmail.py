import base64
from email.mime.text import MIMEText
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from requests import HTTPError


def send_gmail(user, subject, message):
    SCOPES = [
        "https://www.googleapis.com/auth/gmail.send"
    ]
    flow = InstalledAppFlow.from_client_secrets_file('apps/common/fixtures/secret.json', SCOPES)
    creds = flow.run_local_server(open_browser=True)

    service = build('gmail', 'v1', credentials=creds)
    message = MIMEText(message)
    message['to'] = user
    message['subject'] = subject
    create_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

    try:
        message = (service.users().messages().send(userId="me", body=create_message).execute())
        print(F'sent message to {message} Message Id: {message["id"]}')
    except HTTPError as error:
        print(F'An error occurred: {error}')
