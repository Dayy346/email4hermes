# Email Assistant MVP

A small FastAPI backend for a personal email copilot.

## What it does

- Lists recent emails from a demo inbox
- Generates reply drafts from the selected email
- Marks replies as sent in the demo backend
- Creates meeting scheduling proposals
- Is structured so Gmail + Google Calendar can be added later

## Important note

This MVP is intentionally built around **OAuth-style provider integrations** and demo in-memory services.
That means you can wire in real Gmail/Google Calendar access later without storing passwords in the app.

## Tech stack

- FastAPI
- Pydantic Settings
- pytest
- Uvicorn

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
cp .env.example .env
uvicorn email_assistant.main:app --reload
```

Then open:
- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/health

## Run tests

```bash
pytest
```

## API

- `GET /health`
- `GET /emails`
- `GET /emails/{email_id}`
- `POST /emails/{email_id}/draft`
- `POST /emails/{email_id}/send`
- `POST /meetings/schedule`

## Next steps for real email access

Recommended production path:

1. Add Google OAuth with the minimum scopes needed
2. Store refresh tokens securely in a secrets manager
3. Replace the in-memory provider with a Gmail adapter
4. Add Google Calendar support for meeting creation
5. Put human approval in front of any auto-send behavior

## Docker

```bash
docker build -t email-assistant .
docker run --rm -p 8000:8000 --env-file .env email-assistant
```
