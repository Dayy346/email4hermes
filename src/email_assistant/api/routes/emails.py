from fastapi import APIRouter, Depends, HTTPException

from email_assistant.core.container import AppContainer
from email_assistant.schemas import DraftReplyRequest, DraftReplyResponse, EmailListResponse, SendReplyRequest, SendReplyResponse
from email_assistant.services.reply import ReplyGenerator

router = APIRouter(prefix="/emails", tags=["emails"])


def get_container() -> AppContainer:
    from email_assistant.main import container

    return container


@router.get("", response_model=EmailListResponse)
def list_emails(container: AppContainer = Depends(get_container)) -> EmailListResponse:
    return EmailListResponse(items=container.email_service.list_emails())


@router.get("/{email_id}")
def get_email(email_id: str, container: AppContainer = Depends(get_container)) -> dict:
    email = container.email_service.get_email(email_id)
    if email is None:
        raise HTTPException(status_code=404, detail="Email not found")
    return email.model_dump()


@router.post("/{email_id}/draft", response_model=DraftReplyResponse)
def draft_reply(
    email_id: str,
    request: DraftReplyRequest,
    container: AppContainer = Depends(get_container),
) -> DraftReplyResponse:
    email = container.email_service.get_email(email_id)
    if email is None:
        raise HTTPException(status_code=404, detail="Email not found")

    draft = container.reply_generator.generate(email=email, tone=request.tone)
    container.email_service.draft_reply(email_id=email_id, draft=draft)
    return DraftReplyResponse(email_id=email_id, draft=draft)


@router.post("/{email_id}/send", response_model=SendReplyResponse)
def send_reply(
    email_id: str,
    request: SendReplyRequest,
    container: AppContainer = Depends(get_container),
) -> SendReplyResponse:
    email = container.email_service.get_email(email_id)
    if email is None:
        raise HTTPException(status_code=404, detail="Email not found")

    updated = container.email_service.send_reply(email_id=email_id, reply_text=request.reply_text)
    return SendReplyResponse(email_id=email_id, status="sent", delivered_to=email.sender)
