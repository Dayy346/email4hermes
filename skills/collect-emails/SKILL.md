# Collect Emails

Collect recent newsletter emails from Gmail (or the local demo inbox) and normalize them for the pipeline.

## When to use

- First step of every newsletter run
- Dry-runs to verify inbox access

## Inputs

- Read `config/newsletter.yaml`: `lookback_days`, `max_results`, `gmail_query`, `api_base_url`, `sender_allowlist`
- Secrets from `.env` (never print refresh tokens)

## Procedure

1. Ensure API is up at `api_base_url`.
2. `POST {api_base_url}/newsletter/collect` with:
   ```json
   {
     "lookback_days": <lookback_days>,
     "max_results": <max_results>,
     "query": <gmail_query or null>
   }
   ```
3. If `sender_allowlist` is non-empty, keep only messages whose `sender` contains an allowlisted substring (case-insensitive).
4. Write `output/collect.json` with the filtered `items` array.

## Output schema

Each item:

```json
{
  "id": "string",
  "sender": "string",
  "subject": "string",
  "body": "string",
  "links": ["https://..."],
  "received_at": "ISO-8601"
}
```

File: `output/collect.json`

```json
{
  "query": "string",
  "count": 0,
  "items": []
}
```

## Failure behavior

- If API is down: start `uvicorn email_assistant.main:app --host 127.0.0.1 --port 8000` and retry once.
- If auth fails (`handoff_ready` false): stop and tell the user to complete OAuth (`docs/HERMES_ORCHESTRATOR.md`).
- If `count` is 0: write empty `items` and stop the pipeline cleanly (no send).
