from fastapi import APIRouter, Depends, HTTPException

from email_assistant.core.container import AppContainer
from email_assistant.schemas import (
    NewsletterCollectRequest,
    NewsletterCollectResponse,
    NewsletterSendRequest,
    NewsletterSendResponse,
)

router = APIRouter(prefix="/newsletter", tags=["newsletter"])


def get_container() -> AppContainer:
    from email_assistant.main import container

    return container


@router.post("/collect", response_model=NewsletterCollectResponse)
def collect_newsletters(
    request: NewsletterCollectRequest,
    container: AppContainer = Depends(get_container),
) -> NewsletterCollectResponse:
    items, query = container.newsletter_service.collect(
        lookback_days=request.lookback_days,
        max_results=request.max_results,
        query=request.query,
    )
    return NewsletterCollectResponse(items=items, query=query, count=len(items))


@router.post("/send", response_model=NewsletterSendResponse)
def send_newsletter(
    request: NewsletterSendRequest,
    container: AppContainer = Depends(get_container),
) -> NewsletterSendResponse:
    if not request.to_email.strip():
        raise HTTPException(status_code=400, detail="to_email is required")
    if not request.body_text.strip():
        raise HTTPException(status_code=400, detail="body_text is required")

    result = container.newsletter_service.send(
        to_email=request.to_email.strip(),
        subject=request.subject.strip() or "Hermes Personalized Newsletter",
        body_text=request.body_text,
    )
    message_id = result.get("id")
    return NewsletterSendResponse(
        status="sent",
        to_email=request.to_email.strip(),
        subject=request.subject.strip() or "Hermes Personalized Newsletter",
        message_id=message_id if isinstance(message_id, str) else None,
    )
