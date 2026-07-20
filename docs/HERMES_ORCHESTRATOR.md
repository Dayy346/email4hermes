# Hermes Orchestrator — Personalized Newsletter

This doc tells Hermes (and humans) how to run the full pipeline end-to-end.

## Architecture

```text
Inbox (Gmail)
  -> collect-emails
  -> categorize-news
  -> summarize-news
  -> rank-news
  -> research-news
  -> personalize-newsletter
  -> Email gateway (POST /newsletter/send)
```

Application code lives in `src/`. Intelligence and orchestration live in `skills/`.

## Prerequisites

1. Dedicated (or personal) Gmail inbox subscribed to trusted newsletters:
   - [TLDR Tech](https://tldr.tech/)
   - [The Batch](https://www.deeplearning.ai/the-batch/)
   - [ByteByteGo](https://bytebytego.com/)
   - [The Pragmatic Engineer](https://newsletter.pragmaticengineer.com/)
   - [Ben's Bites](https://www.bensbites.co/)
2. Google Cloud OAuth client (Web application) with Gmail API enabled
3. Redirect URI exactly: `http://localhost:8000/auth/google/callback`
4. Python 3.11+ and this repo installed (`pip install -e .[dev]`)

## Env mapping

Deck slides may say `GMAIL_*`. This repo uses:

| Deck name | Repo `.env` key |
|-----------|-----------------|
| GMAIL_CLIENT_ID | `GOOGLE_CLIENT_ID` |
| GMAIL_CLIENT_SECRET | `GOOGLE_CLIENT_SECRET` |
| GMAIL_REFRESH_TOKEN | `GOOGLE_REFRESH_TOKEN` |
| NEWSLETTER_EMAIL | `GOOGLE_ACCOUNT_EMAIL` + `config/newsletter.yaml` `to_email` |

Also set `EMAIL_BACKEND=gmail` for live Gmail collect/send.

## One-time setup

1. Copy `.env.example` → `.env` and fill Google credentials.
2. Run OAuth to obtain `GOOGLE_REFRESH_TOKEN` (`GET /auth/google/url` → consent → callback JSON).
3. Edit `config/newsletter.yaml`:
   - `cadence_days` (default 3)
   - `profile` (`junior` | `senior` | `custom`)
   - `to_email`
   - `timezone`
4. Paste `docs/HERMES_MASTER_PROMPT.md` into Hermes and let it install the recurring job.
5. Dry-run: `POST /newsletter/collect` then a full skill chain without send (or send to yourself once).

## Cron / schedule

Hermes should create a job that every `cadence_days` days:

1. Ensures the API is up (or starts it)
2. Runs `skills/run-newsletter` (entrypoint skill)
3. Logs results under `output/`

Example Linux cron (if Hermes cannot schedule natively), for a 3-day cadence at 09:00 in local time — adjust to your timezone and Hermes CLI:

```cron
0 9 */3 * * cd /path/to/email4hermes && hermes run skills/run-newsletter
```

Prefer Hermes' own scheduler when available; treat the line above as a fallback.

## API helpers

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/auth/google/status` | OAuth / handoff readiness |
| GET | `/auth/google/url` | Authorization URL |
| GET | `/auth/google/callback` | Exchanges code → tokens (includes refresh_token) |
| POST | `/newsletter/collect` | Pull recent inbox messages for the pipeline |
| POST | `/newsletter/send` | Send a composed briefing (not a reply) |

### Collect body

```json
{
  "lookback_days": 3,
  "max_results": 25,
  "query": null
}
```

### Send body

```json
{
  "to_email": "you@example.com",
  "subject": "Hermes Personalized Newsletter",
  "body_text": "..."
}
```

## Skill order

See each `skills/*/SKILL.md`. Cron always enters through `skills/run-newsletter`.

## Dry-run smoke checklist

- [ ] `GET /health` → `{"status":"ok"}`
- [ ] `GET /auth/google/status` → `handoff_ready: true` when using Gmail
- [ ] `POST /newsletter/collect` returns items or `count: 0`
- [ ] Skill chain writes artifacts under `output/`
- [ ] `POST /newsletter/send` delivers briefing to `to_email`
- [ ] Recurring job exists for `cadence_days`
