from typing import Any, List, Optional

from fastapi import HTTPException
from pydantic import BaseModel, field_validator

from ..Agentic.Graph import workflow
from langchain_core.tools import tool
from ..email import email_read,email_Send


class Send_Email_Input(BaseModel):
    to: str
    subject: str
    body: str
    attachments: Optional[List[dict]] = None

    @field_validator("attachments", mode="before")
    @classmethod
    def fix_attachments(cls, v: Any):
        if v in ["None", "", "null"]:
            return None
        return v
@tool()
async def rag_retrival(query: str,Thread: int = 1):
    """
    This tool performs hybrid retrieval (semantic + BM25) over indexed content and generates answers using LLMs.

    Parameters
    ----------
    query : Query
        The query object containing the user query, thread, and other relevant information.

    Returns
    -------
    result : str
        The generated answer.
    """
    try:
        config={"configurable": {"thread_id": Thread}}
        initial_state={"USER_QUERY":query}
        result=await workflow.ainvoke(initial_state,config=config) # type: ignore
    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": "Error in processing query", "error": str(e)})
    return result.get('LLM_RESPONSE','')

@tool()
async def read_emails():
    """
    This tool reads the latest emails from the user's Gmail account and returns a structured list of email details.

    Returns
    -------
    email_list : dict
        A dictionary containing email details such as subject, sender, body, and attachments.
    """
    try:
        email_list = await email_read.read_emails()
    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": "Error in reading emails", "error": str(e)})
    return email_list
@tool(args_schema=Send_Email_Input)
async def send_emails(
    to: str,
    subject: str,
    body: str,
    attachments: Optional[List[dict]] = None
):
    """
    This tool sends an email to the specified recipient with the given subject and body.

    Parameters
    ----------
    to : str
        The recipient's email address.
    subject : str
        The email's subject.
    body : str
        The email's body.
    attachments : Optional[List[dict]], optional
        A list of dictionaries containing the filename and content of the attachments.

    Returns
    -------
    dict
        A dictionary containing a message indicating whether the email was sent successfully.

    Raises
    ------
    HTTPException
        If an error occurs while sending the email.
    """
    if attachments == []:
        attachments = None
    print(f"=== Sending email to: {to}, subject: {subject}, body: {body}, attachments: {attachments} ===")

    try:
        await email_Send.send_email(
            to=to,
            subject=subject,
            body=body,
            attachments=attachments
        )
        return {"messages": "Email sent successfully"}
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"message": "Error in sending email", "error": str(e)}
        )