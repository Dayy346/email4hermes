# Hermes Master Prompt — Personalized Newsletter

Copy everything below the line into Hermes after cloning this repo and filling `.env`.

---

You are setting up and operating the **email4hermes Personalized Newsletter** pipeline in this repository.

## Your jobs

1. **One-time setup** (do this first if cron is not already installed)
2. **Recurring run** every `cadence_days` from `config/newsletter.yaml`

## Setup checklist

1. Read `config/newsletter.yaml` and `docs/HERMES_ORCHESTRATOR.md`.
2. Read `.env` / `.env.example`. Required secrets (never commit them):
   - `GOOGLE_CLIENT_ID`
   - `GOOGLE_CLIENT_SECRET`
   - `GOOGLE_REFRESH_TOKEN`
   - `GOOGLE_ACCOUNT_EMAIL` (mailbox owner)
   - `EMAIL_BACKEND=gmail`
   - `GOOGLE_REDIRECT_URI` (default `http://localhost:8000/auth/google/callback`)
3. If `GOOGLE_REFRESH_TOKEN` is missing:
   - Start the API: `uvicorn email_assistant.main:app --host 127.0.0.1 --port 8000`
   - Open `GET /auth/google/url`, complete Google consent, copy `refresh_token` from `/auth/google/callback` into `.env`
4. Ask the user **only** for missing fill-ins in `config/newsletter.yaml`:
   - `cadence_days` (default **3**)
   - `profile` (`junior` | `senior` | `custom`)
   - `to_email` (who receives the briefing; usually the same as `GOOGLE_ACCOUNT_EMAIL`)
   - `timezone`
5. Write those values into `config/newsletter.yaml`.
6. Install or update a recurring job that runs the newsletter pipeline every `cadence_days` days in `timezone`. Prefer Hermes cron / scheduled tasks. On Linux you may also use system cron calling a Hermes skill run for `skills/run-newsletter`.
7. Confirm the API is reachable at `api_base_url` from config (default `http://127.0.0.1:8000`).
8. Run one **dry-run**: execute `skills/run-newsletter` with send disabled or confirm collect returns items / empty inbox message. Then offer a live send.

## Every scheduled run

Execute skills **in this order**, using each skill's `SKILL.md` as the contract:

1. `skills/collect-emails`
2. `skills/categorize-news`
3. `skills/summarize-news`
4. `skills/rank-news`
5. `skills/research-news`
6. `skills/personalize-newsletter`
7. Send via `POST {api_base_url}/newsletter/send` with `to_email`, subject, and final body

Persist intermediate JSON/Markdown under `output/` (from config). Do not commit secrets. If there are no new newsletters, send nothing (or a short "no new stories" note only if the user asked for that).

## Fill-in values (edit in config, not here)

- Cadence days: read `cadence_days` from `config/newsletter.yaml`
- Profile: read `profile`
- Delivery email: read `to_email`

When setup is complete, reply with: cadence, next run time, profile, delivery email, and whether the dry-run succeeded.
