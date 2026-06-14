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

## Google OAuth setup

To connect a real Gmail account, create a Google Cloud OAuth client for a Web application and set:

- GOOGLE_CLIENT_ID
- GOOGLE_CLIENT_SECRET
- GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback
- GOOGLE_SCOPES=https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/gmail.send https://www.googleapis.com/auth/calendar.events
- GOOGLE_REFRESH_TOKEN once the account has authorized the app
- GOOGLE_ACCOUNT_EMAIL if you want the app to display the mailbox owner explicitly

Useful status endpoints:

- `GET /auth/google/status` — shows whether OAuth + handoff fields are ready
- `GET /auth/google/url` — returns the Google authorization URL when config is present

The app is currently scaffolded to generate the Google authorization URL, but it still uses the in-memory demo email provider until the Gmail adapter is added.

## Handoff checklist

Before I can manage the real mailbox, I need these values in `.env` or another secret store:

1. `GOOGLE_CLIENT_ID`
2. `GOOGLE_CLIENT_SECRET`
3. `GOOGLE_REDIRECT_URI`
4. `GOOGLE_REFRESH_TOKEN`
5. `GOOGLE_ACCOUNT_EMAIL` (optional but helpful)
6. `GOOGLE_SCOPES` if you want to customize access

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
