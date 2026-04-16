import asyncio
import base64
import traceback
from fastapi import HTTPException
from ..email.authenticate_gmail_api import authenticate_gmail_api
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from html import unescape
from Logger import logger
from bs4 import BeautifulSoup
import re
async def read_emails()->dict:
    email_list = {}
    creds=await authenticate_gmail_api() # type: ignore
    try:
        service = build('gmail', 'v1', credentials=creds)
        result= service.users().messages().list(userId='me', maxResults=10).execute()
        messages=result.get('messages', [])
        for msg in messages:
            msg_id=msg['id']
            txt=service.users().messages().get(userId='me', id=msg['id']).execute()
            try:
                payload=txt['payload']
                headers=payload['headers']
                subject=""
                sender=""
                for d in headers:
                    if d['name']=='Subject':
                        subject=d['value']
                    if d['name']=='From':
                        sender=d['value']
                    if d['name']=='Date':
                        time=(d['value'])
                body_text,attachments = await get_email_body(payload)          
                email_list[msg_id] = {
                    'subject': subject,
                    'sender': sender,
                    'body': body_text,
                    'attachments': attachments
                }
            except Exception as e:
                logger.error(f"Error processing email ID {msg['id']}: error:{e} traceback:{traceback.format_exc()}")
                raise HTTPException(status_code=500, detail={"message": f"Error processing email ID {msg['id']}, traceback: {traceback.format_exc()}", "error": str(e)})
        return email_list
    except HttpError as error:
        logger.error(f'An error occurred: {error}')
        return {}

async def get_email_body(payload):
    attachments = {}
    def decode_data(data):
        data = data.replace("-", "+").replace("_", "/")
        padding = 4 - len(data) % 4
        if padding != 4:
            data += "=" * padding
        decoded = base64.b64decode(data).decode('utf-8', errors='replace')
        return decoded

    def html_to_text(html):
        soup = BeautifulSoup(html, 'html.parser')
        for tag in soup(['script', 'style', 'head']):
            tag.decompose()
        text = soup.get_text(separator='\n')
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

    def extract_from_parts(parts):
        plain = None
        html = None
        
        for part in parts:
            mime = part.get('mimeType', '')
            if mime.startswith('multipart'):
                sub_plain, sub_html, sub_attachments = extract_from_parts(part.get('parts', []))
                plain = plain or sub_plain
                html = html or sub_html
                attachments.update(sub_attachments)
            elif mime == 'text/plain':
                data = part.get('body', {}).get('data', '')
                if data:
                    plain = decode_data(data)
            elif mime == 'text/html':
                data = part.get('body', {}).get('data', '')
                if data:
                    html = decode_data(data)
            if "attachmentId" in part.get('body', {}):
                attachments[part['body']['attachmentId']] = {
                    'filename': part.get('filename', ''),
                    'mimeType': part.get('mimeType', '')
                }
        return plain, html, attachments 

    parts = payload.get('parts', [])
    if parts:
        plain, html,attachments = extract_from_parts(parts)
        if plain:
            return clean_body(plain),attachments
        if html:
            return clean_body(html_to_text(html)),attachments

    data = payload.get('body', {}).get('data', '')
    if "attachmentId" in payload.get('body', {}):
        attachments[payload['body']['attachmentId']] = {
            'filename': payload.get('filename', ''),
            'mimeType': payload.get('mimeType', '')
        }
    
    if data:
        raw = decode_data(data)
        if payload.get('mimeType', '') == 'text/html' or raw.strip().startswith('<'):
            return clean_body(html_to_text(raw)),attachments
        return raw,attachments

    return "",attachments


def clean_body(text):
    text = unescape(text)
    text = re.sub(r'[\u034f\u2007\ufeff\u200b\u200c\u200d\u00ad\u200c]+', '', text)
    text = text.replace('\u200c', '')
    text = text.replace('\xa0', ' ')
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    text = re.sub(r' {2,}', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()
    
if __name__ == '__main__':
    result=asyncio.run(read_emails())   
    print(result)