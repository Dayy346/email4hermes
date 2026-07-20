# Run Newsletter

Cron entrypoint. Runs the full personalized newsletter pipeline and emails the briefing.

## When to use

- Hermes scheduled / cron jobs
- Manual "run the newsletter now"
- After setup from `docs/HERMES_MASTER_PROMPT.md`

## Inputs

- `config/newsletter.yaml`
- `.env` with Google handoff when `EMAIL_BACKEND=gmail`

## Procedure

1. Read config: `cadence_days`, `profile`, `to_email`, `api_base_url`, `output_dir`, `lookback_days`.
2. Create `output/` if missing.
3. Run skills in order (follow each `SKILL.md`):
   1. `skills/collect-emails`
   2. Stop early if collect `count == 0` (log and exit 0 unless user wants empty notifications).
   3. `skills/categorize-news`
   4. `skills/summarize-news`
   5. `skills/rank-news`
   6. `skills/research-news`
   7. `skills/personalize-newsletter`
4. Send (unless `dry_run=true` was requested):
   - `POST {api_base_url}/newsletter/send`
   ```json
   {
     "to_email": "<to_email from config>",
     "subject": "<from personalize.json or default>",
     "body_text": "<contents of output/briefing.txt>"
   }
   ```
5. Write `output/last_run.json` with timestamps, counts, message_id, and success flag.

## Scheduling

When installing the recurring job, schedule every `cadence_days` days in `timezone` from config. Re-read config on each run so cadence changes apply without rewriting the skill.

## Failure behavior

- Missing `to_email`: abort send and ask user to fill `config/newsletter.yaml`.
- Send failure: keep `output/briefing.*` and report the API error; do not delete artifacts.
- Partial pipeline failure: stop at the failing skill; do not send a half-built briefing.

## Success criteria

- Briefing email delivered to `to_email`, or dry-run completed with artifacts under `output/`
