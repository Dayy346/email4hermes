from fastapi import APIRouter, Depends

from email_assistant.core.container import AppContainer
from email_assistant.schemas import ScheduleMeetingRequest, ScheduleMeetingResponse

router = APIRouter(prefix="/meetings", tags=["meetings"])


def get_container() -> AppContainer:
    from email_assistant.main import container

    return container


@router.post("/schedule", response_model=ScheduleMeetingResponse)
def schedule_meeting(
    request: ScheduleMeetingRequest,
    container: AppContainer = Depends(get_container),
) -> ScheduleMeetingResponse:
    return container.meeting_scheduler.schedule(request)
