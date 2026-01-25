# ZABAL Context Updater

Keep your AI voice consistent by updating `memory/personality.json` with evidence from your recent writing.

## What It Does

Analyzes your recent Paragraph posts, Farcaster casts, or X posts and:
- Extracts voice patterns
- Adds new voice examples (max 1-2 per run)
- Identifies phrases to avoid
- Updates style notes
- Tracks your current state/phase

## Hard Rules

✅ **Does:**
- Evidence-based updates only
- Minimal, high-signal edits
- Automatic backups before changes
- Safety checks (no marketing language, no bloat)

❌ **Never:**
- Adds marketing/motivational language
- Contradicts existing voice examples
- Stores sensitive personal data
- Rewrites the whole file

## Usage

### Interactive CLI

```bash
python3 update_context.py
```

Follow the prompts:
1. Enter URLs or paste text from recent writing
2. Optionally describe what felt "off"
3. Confirm and run

### Programmatic

```python
from src.context_updater import ZABALContextUpdater

updater = ZABALContextUpdater()

sources = [
    "https://paragraph.com/@thezao/day-25",
    "Today was steady. Not flashy, just present..."
]

result = updater.update_from_sources(
    sources=sources,
    feedback="Felt too formal in recent outputs",
    dry_run=False  # Set True to preview without saving
)

print(result["edit_summary"])
print(result["reasoning"])
```

## Output Format

```
EDIT SUMMARY
============
✓ Added voice example: Day 25 - Steady Progress
✓ Added voice don't: "optimize"
✓ Updated current state

REASONING
=========
Added Day 25 as it perfectly captures the "quiet momentum" 
pattern with concrete observation → internal shift → grounded 
close. Removed "optimize" as it appeared in 3 recent outputs 
and feels corporate, not Zaal.

NEXT STEP
=========
→ Generate a test newsletter to verify voice consistency

💾 Backup saved: memory/backups/personality_20260125_174530.json
```

## Memory Structure

```json
{
  "voice_examples": [
    {
      "title": "Day 13 - Goa Travel",
      "content": "Today was a travel day...",
      "added": "2026-01-25T17:30:00"
    }
  ],
  "voice_donts": ["Let's dive in", "Game-changer"],
  "style_notes": ["Use em dashes naturally", "Notice small shifts"],
  "context_memories": ["Building ZABAL platform", "Based in Maine"],
  "current_projects": ["ZABAL platform", "Daily newsletter"],
  "current_state": {
    "phase": "build sprint",
    "energy": "medium",
    "focus": ["consistency", "voice refinement", "community"],
    "avoid_this_week": ["over-explaining", "marketing speak"]
  }
}
```

## Safety Checks

Before saving, the updater checks:
- ❌ Too many voice examples (>12)
- ❌ Marketing language detected
- ❌ Contradictions with existing voice
- ❌ Unbounded growth

If any check fails, changes are rejected.

## Backups

Every update creates a timestamped backup:
```
memory/backups/personality_20260125_174530.json
```

Restore if needed:
```bash
cp memory/backups/personality_YYYYMMDD_HHMMSS.json memory/personality.json
```

## Best Practices

1. **Run weekly** - After 5-7 new Day entries
2. **Use real URLs** - Let the AI read your actual writing
3. **Provide feedback** - Note what felt off in recent outputs
4. **Review changes** - Check the edit summary before confirming
5. **Test after** - Generate a newsletter to verify voice

## Integration with Web UI

The Memory & Voice tab in the web UI (`http://127.0.0.1:5000`) lets you:
- View current personality
- Manually add/remove items
- See all voice examples

The Context Updater is for **bulk evidence-based updates** from recent writing.

## Troubleshooting

**"Analysis failed"**
- Check your GROQ_API_KEY in .env
- Verify sources are accessible

**"Safety checks failed"**
- Review the issues listed
- The update was rejected to protect voice quality
- Adjust sources or feedback and try again

**Voice still feels off**
- Add more voice examples manually
- Use the "Improve Prompts" tab in web UI
- Run updater with specific feedback about what's wrong
