# Personalize Newsletter

Render the final briefing for the configured audience profile and prepare the email body.

## When to use

- After `research-news` wrote `output/research.json`

## Inputs

- `output/research.json`
- `config/newsletter.yaml` → `profile`, `custom_profile_notes`, `to_email`

## Profile rules

### junior

- Explain buzzwords briefly
- Define technical concepts in plain language
- Add 1 learning resource link when useful

### senior

- Skip basics
- Focus on engineering impact and implementation details
- Prefer signal over noise; shorter blurbs

### custom

- Follow `custom_profile_notes`

## Procedure

1. Select top stories (typically top 5–10 by score; skip very low confidence).
2. Write Markdown briefing with sections:
   - Title + date
   - Top stories
   - Also noted (optional lower-ranked)
   - Sources
3. Save `output/briefing.md` and `output/briefing.txt` (plain text email body).
4. Hand off to send step in `run-newsletter` (do not send inside this skill unless asked).

## Output

- `output/briefing.md`
- `output/briefing.txt`
- Optional metadata `output/personalize.json`:
  ```json
  {
    "profile": "junior",
    "story_count": 0,
    "subject": "Hermes Personalized Newsletter — YYYY-MM-DD"
  }
  ```

## Failure behavior

- If research array is empty: write a short "No new stories in lookback window" briefing and set `story_count: 0`.
