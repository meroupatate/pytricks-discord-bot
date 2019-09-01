import base64
import email
import pickle
from datetime import timedelta
from os import getenv

import requests
from dotenv import load_dotenv
from googleapiclient.discovery import build
from time import sleep
from timeloop import Timeloop

load_dotenv()
webhook = getenv('DISCORD_WEBHOOK')
tl = Timeloop()


@tl.job(interval=timedelta(seconds=10))
def main():
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
    service = build('gmail', 'v1', credentials=creds)

    messages = get_new_pytricks(service)

    if not len(messages):
        print('No new messages found.')
    else:
        print(f'Found {len(messages)} new message(s)')
        for message in messages:
            subject, content = get_content(message)
            print(subject)
            status_code = send_to_webhook(subject, content)
            if status_code == 204:
                mark_as_read(service, message)


def get_new_pytricks(service):
    results = service.users().messages().list(userId='me', labelIds=['INBOX', 'UNREAD'],
                                              q='from:info@realpython.com subject:[🐍pytricks]').execute()
    messages = results.get('messages', [])
    if not messages:
        return []
    else:
        return [service.users().messages().get(userId='me', id=message['id'], format='raw').execute() for message in
                messages]


def get_content(message):
    msg = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
    mime_msg = email.message_from_bytes(msg)
    messageMainType = mime_msg.get_content_maintype()
    messageSubject = email.header.decode_header(mime_msg['subject'])[0][0].decode()
    if messageMainType == 'multipart':
        messageContent = ""
        for part in mime_msg.get_payload():
            if part.get_content_maintype() == 'text':
                messageContent = part.get_payload(decode=True).decode()
                break
    elif messageMainType == 'text':
        messageContent = mime_msg.get_payload(decode=True).decode()
    return messageSubject, messageContent


def mark_as_read(service, message):
    msgId = message['id']
    body = {"removeLabelIds": ["UNREAD"]}
    response = service.users().messages().modify(userId='me', id=msgId, body=body).execute()
    print('Marked as read')


def send_to_webhook(subject, content):
    data = {'content': f'**{subject}**\n```python\n{content.split("------")[0]}```\n'}
    response = requests.post(webhook, json=data)
    print('Sent to discord')
    return response.status_code


tl.start()
while True:
    try:
        sleep(1)
    except KeyboardInterrupt:
        tl.stop()
        break
