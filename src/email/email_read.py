import asyncio
import traceback
from fastapi import HTTPException
from ..email.authenticate_gmail_api import authenticate_gmail_api
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from html import unescape
from bs4 import BeautifulSoup

async def read_emails():
    email_list = {}
    creds=await authenticate_gmail_api()
    try:
        service = build('gmail', 'v1', credentials=creds)
        result= service.users().messages().list(userId='me', maxResults=5).execute()
        messages=result.get('messages', [])
        for msg in messages:
            txt=service.users().messages().get(userId='me', id=msg['id']).execute()
            try:
                payload=txt['payload']
                debug_payload(payload)
                headers=payload['headers']
                subject=""
                sender=""
                time=""
                for d in headers:
                    if d['name']=='Subject':
                        subject=d['value']
                    if d['name']=='From':
                        sender=d['value']
                    if d['name']=='Date':
                        time=(d['value'])
                body_text = await get_email_body(payload)
                attachments = []           
                print(f"Subject: {subject}")
                print(f"From: {sender}")
                print(f"Body: {body_text}")
                email_list[time] = {
                    'subject': subject,
                    'sender': sender,
                    'body': body_text,
                    'attachments': attachments
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail={"message": f"Error processing email ID {msg['id']}, traceback: {traceback.format_exc()}", "error": str(e)})
        return email_list
    except HttpError as error:
        print(f'An error occurred: {error}')
        return []
def debug_payload(payload, depth=0):
    indent = "  " * depth
    mime = payload.get('mimeType', 'unknown')
    body = payload.get('body', {})
    data = body.get('data', '')
    for part in payload.get('parts', []):
        debug_payload(part, depth + 1)

# Call this before get_email_body
async def get_email_body(payload):

    def decode_data(data):
        import base64
        # Fix URL-safe base64 chars
        data = data.replace("-", "+").replace("_", "/")
        # Fix padding
        padding = 4 - len(data) % 4
        if padding != 4:
            data += "=" * padding
        decoded = base64.b64decode(data).decode('utf-8', errors='replace')
        return decoded

    def html_to_text(html):
        import re
        soup = BeautifulSoup(html, 'html.parser')
        for tag in soup(['script', 'style', 'head']):
            tag.decompose()
        text = soup.get_text(separator='\n')
        # Collapse excessive blank lines
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

    def extract_from_parts(parts):
        plain = None
        html = None
        for part in parts:
            mime = part.get('mimeType', '')
            if mime.startswith('multipart'):
                sub_plain, sub_html = extract_from_parts(part.get('parts', []))
                plain = plain or sub_plain
                html = html or sub_html
            elif mime == 'text/plain':
                data = part.get('body', {}).get('data', '')
                if data:
                    plain = decode_data(data)
            elif mime == 'text/html':
                data = part.get('body', {}).get('data', '')
                if data:
                    html = decode_data(data)
        return plain, html

    parts = payload.get('parts', [])
    if parts:
        plain, html = extract_from_parts(parts)
        if plain:
            return clean_body(plain)
        if html:
            return clean_body(html_to_text(html))

    data = payload.get('body', {}).get('data', '')
    
    if data:
        raw = decode_data(data)
        if payload.get('mimeType', '') == 'text/html' or raw.strip().startswith('<'):
            return clean_body(html_to_text(raw))
        return raw

    return ""
import re

def clean_body(text):
    # Unescape HTML entities (&nbsp; &zwnj; etc)
    text = unescape(text)
    # Remove zero-width and invisible unicode characters (includes &zwnj; after unescaping)
    text = re.sub(r'[\u034f\u2007\ufeff\u200b\u200c\u200d\u00ad\u200c]+', '', text)
    # Remove zero-width non-joiner specifically (what &zwnj; becomes)
    text = text.replace('\u200c', '')
    # Replace non-breaking spaces with regular spaces (what &nbsp; becomes)
    text = text.replace('\xa0', ' ')
    # Normalize Windows line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    # Collapse multiple spaces into one
    text = re.sub(r' {2,}', ' ', text)
    # Collapse multiple newlines into max 2
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()
    
if __name__ == '__main__':
    result=asyncio.run(read_emails())   
    print(result)