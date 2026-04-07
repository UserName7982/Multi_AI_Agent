from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
import mimetypes
from email.message import EmailMessage

from src.email.authenticate_gmail_api import authenticate_gmail_api

async def send_email(to, subject, body, attachments=None):
    cred=await authenticate_gmail_api()
    mimemessage = EmailMessage()
    try:
        service=build('gmail', 'v1', credentials=cred)
        mimemessage["To"] = to
        mimemessage["Subject"] = subject
        mimemessage.set_content(body)
        if attachments is not None:
            for attachment in attachments:
                filename = attachment['filename']
                mime_type, _ = mimetypes.guess_type(filename)
                if mime_type is None:
                    mime_type = 'application/octet-stream'
                maintype, subtype = mime_type.split('/', 1)
                mimemessage.add_attachment(attachment['content'], maintype=maintype, subtype=subtype, filename=filename)
        encoded_message = base64.urlsafe_b64encode(mimemessage.as_bytes()).decode()
        send_body = {
    "raw": encoded_message
}
        send_message=service.users().messages().send(userId="me", body=send_body).execute()
        return {"message": "Email sent successfully", "sentId": send_message['id']}
    except HttpError as error:
        print(f'An error occurred: {error}')
        return {"message": f"Failed to create email message: {str(error)}"}