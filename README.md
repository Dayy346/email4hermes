# Email4Hermes — Personalized Newsletter MVP

FastAPI Gmail backend + Hermes skills that turn newsletter inbox mail into a personalized briefing and email it on a schedule.

## What it does

- Connects a Gmail inbox via OAuth (read + send)
- Collects recent newsletter emails through `POST /newsletter/collect`
- Runs a Hermes skill pipeline: collect → categorize → summarize → rank → research → personalize
- Emails the finished briefing via `POST /newsletter/send`
- Uses a master prompt so Hermes can fill cadence/profile and install its own cron job

## Layout

```text
email4hermes/
├── src/                 # FastAPI + Gmail provider
├── skills/              # Hermes SKILL.md pipeline
├── config/newsletter.yaml
├── docs/
│   ├── HERMES_MASTER_PROMPT.md
│   └── HERMES_ORCHESTRATOR.md
├── install.sh
└── README.md
```

## Quick start

### Linux / macOS

```bash
./install.sh
source .venv/bin/activate
uvicorn email_assistant.main:app --reload
```

### Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
Copy-Item .env.example .env
# edit .env, then:
.\.venv\Scripts\python.exe -m uvicorn email_assistant.main:app --reload
```

Then open:

- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/health

## Hermes setup (important)

1. Fill Google OAuth values in `.env` (see below).
2. Edit `config/newsletter.yaml` (`cadence_days`, `profile`, `to_email`).
3. Paste **[docs/HERMES_MASTER_PROMPT.md](docs/HERMES_MASTER_PROMPT.md)** into Hermes.
4. Hermes will confirm missing fill-ins, install a recurring job every `cadence_days`, and run `skills/run-newsletter`.

Full orchestrator notes: [docs/HERMES_ORCHESTRATOR.md](docs/HERMES_ORCHESTRATOR.md)

## Google OAuth / env

Create a Google Cloud OAuth **Web** client, enable Gmail API, set redirect URI:

`http://localhost:8000/auth/google/callback`

Set in `.env`:

```env
EMAIL_BACKEND=gmail
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback
GOOGLE_REFRESH_TOKEN=...
GOOGLE_ACCOUNT_EMAIL=you@example.com
```

Get the refresh token:

1. Start the API
2. Open `GET /auth/google/url`
3. Complete consent
4. Copy `refresh_token` from `/auth/google/callback` into `.env`

Deck `GMAIL_*` names map to `GOOGLE_*` in this repo (see orchestrator doc).

## Suggested newsletter subscriptions

Subscribe the inbox to:

- [TLDR Tech](https://tldr.tech/)
- [The Batch](https://www.deeplearning.ai/the-batch/)
- [ByteByteGo](https://bytebytego.com/)
- [The Pragmatic Engineer](https://newsletter.pragmaticengineer.com/)
- [Ben's Bites](https://www.bensbites.co/)

## API

- `GET /health`
- `GET /emails` / `GET /emails/{id}` / draft + send reply
- `POST /meetings/schedule`
- `GET /auth/google/status` / `/url` / `/callback`
- `POST /newsletter/collect`
- `POST /newsletter/send`

Set `EMAIL_BACKEND=gmail` and complete handoff fields to use the live Gmail provider; otherwise demo in-memory data is used.

## Skills

| Skill | Role |
|-------|------|
| `collect-emails` | Pull + normalize inbox messages |
| `categorize-news` | Topics + entities |
| `summarize-news` | Structured summaries |
| `rank-news` | Score + dedupe |
| `research-news` | Validate top stories |
| `personalize-newsletter` | Profile-aware briefing |
| `run-newsletter` | Cron entrypoint + send |

## Tests

```bash
pytest
```

## Docker

```bash
docker build -t email-assistant .
docker run --rm -p 8000:8000 --env-file .env email-assistant
```
