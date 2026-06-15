from fastapi import FastAPI

from email_assistant.api.routes.auth import router as auth_router
from email_assistant.api.routes.emails import router as emails_router
from email_assistant.api.routes.health import router as health_router
from email_assistant.api.routes.meetings import router as meetings_router
from email_assistant.core.container import AppContainer
from email_assistant.core.config import get_settings

settings = get_settings()
container = AppContainer()

app = FastAPI(title=settings.app_name, version="0.1.0")
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(emails_router)
app.include_router(meetings_router)
