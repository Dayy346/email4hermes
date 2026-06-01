from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4

from email_assistant.schemas import ScheduleMeetingRequest, ScheduleMeetingResponse


class MeetingScheduler:
    def schedule(self, request: ScheduleMeetingRequest) -> ScheduleMeetingResponse:
        raise NotImplementedError


@dataclass(slots=True)
class MockMeetingScheduler(MeetingScheduler):
    base_link: str = "https://meet.google.com/mock-meeting"

    def schedule(self, request: ScheduleMeetingRequest) -> ScheduleMeetingResponse:
        scheduled_time = request.proposed_times[0]
        return ScheduleMeetingResponse(
            meeting_id=f"meeting-{uuid4().hex[:10]}",
            subject=request.subject,
            attendees=request.attendees,
            scheduled_time=scheduled_time,
            duration_minutes=request.duration_minutes,
            meeting_link=f"{self.base_link}/{uuid4().hex[:8]}",
        )
