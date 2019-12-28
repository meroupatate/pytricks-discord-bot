import base64
import email
import pickle
from datetime import timedelta
from os import getenv
from typing import Dict, List, Tuple

import googleapiclient.discovery
import requests
from dotenv import load_dotenv
from structlog import get_logger
from timeloop import Timeloop

load_dotenv()
webhook = getenv('DISCORD_WEBHOOK')
tl = Timeloop()
log = get_logger()


def get_new_pytricks(service: googleapiclient.discovery.Resource) -> List[Dict]:
    results = service.users().messages().list(userId='me', labelIds=['INBOX', 'UNREAD'],
            q='from:info@realpython.com subject:[🐍pytricks]').execute()
    messages = results.get('messages', [])
    return [service.users().messages().get(userId='me', id=msg['id'], format='raw').execute() for msg in messages]


def extract_message_content(mime_msg: email.message.Message) -> str:
    for part in mime_msg.get_payload():
        if part.get_content_maintype() == 'text':
            return part.get_payload(decode=True).decode()
    return ''


def get_content(message: Dict) -> Tuple[str, str]:
    msg = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
    mime_msg = email.message_from_bytes(msg)
    messageMainType = mime_msg.get_content_maintype()
    messageSubject = email.header.decode_header(mime_msg['subject'])[0][0].decode()

    if messageMainType == 'multipart':
        messageContent = extract_message_content(mime_msg)
    elif messageMainType == 'text':
        messageContent = mime_msg.get_payload(decode=True).decode()
    return messageSubject, messageContent


def mark_as_read(service: googleapiclient.discovery.Resource, message: Dict) -> None:
    msgId = message['id']
    body = {"removeLabelIds": ["UNREAD"]}
    response = service.users().messages().modify(userId='me', id=msgId, body=body).execute()
    log.info('Marked as read', response=response)


def send_to_webhook(subject: str, content: str) -> requests.models.Response:
    subject = subject.replace('_', '\_').replace('*', '\*')
    data = {'content': f'**{subject}**\n```python\n{content.split("------")[0]}```\n'}
    log.info('Sent to discord', subject=subject)
    return requests.post(webhook, json=data)


def split_message(message: str) -> List[str]:
    parts = []
    lines = message.split('\n')
    part = ''
    for line in lines:
        if len(part + line) < 2000:
            part += line
        else:
            parts.append(part)
            part = line
    parts.append(part)
    return parts


@tl.job(interval=timedelta(seconds=1800))
def main() -> None:
    with open('token.pickle', 'rb') as token:
        credentials = pickle.load(token)

    service = googleapiclient.discovery.build('gmail', 'v1', credentials=credentials)
    messages = get_new_pytricks(service)

    for message in messages:
        subject, content = get_content(message)
        log.info('Found new message', subject=subject)
        if len(content) < 2000:
            response = send_to_webhook(subject, content)
        else:
            parts = split_message(content)
            for part in parts:
                response = send_to_webhook(subject, part)
        if response.status_code == 204:
            mark_as_read(service, message)
        else:
            log.error(f'Error while sending to Discord: {response.status_code} {response.content}')


if __name__ == '__main__':
    tl.start(block=True)
