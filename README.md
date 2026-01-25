# ZABAL Newsletter Bot

Automated content generator for Year of the ZABAL — daily newsletter and social media content creation using OpenAI's API.

## Features

- **Newsletter Generation**: Automatically creates daily ZABAL newsletter entries with proper formatting, date calculation, and BetterCallZaal's voice
- **Social Content Generation**: Transforms newsletters into platform-native posts for:
  - Twitter/X (main feed + group chat)
  - Farcaster (ZAO channel, general, + community suggestions)
  - Telegram
  - Discord
  - TikTok & YouTube (when video content is included)
- **Interactive Mode**: Guided workflow with prompts
- **CLI Mode**: Command-line interface for automation and scripting
- **Auto-save**: All outputs saved with timestamps
- **Clipboard Support**: One-click copy to clipboard

## Setup

### 1. Install Dependencies

```bash
cd /Users/zaalpanthaki/Documents/ZABALNewsletterBot
pip install -r requirements.txt
```

### 2. Configure OpenAI API

Create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```
OPENAI_API_KEY=sk-your-actual-api-key-here
OPENAI_MODEL=gpt-4o
```

### 3. Make CLI Executable (Optional)

```bash
chmod +x zabal.py
```

## Usage

### Interactive Mode (Recommended)

```bash
python zabal.py interactive
```

Or simply:

```bash
python zabal.py
```

This will guide you through:
1. Choosing what to generate (newsletter, social, or both)
2. Entering your daily input
3. Optionally adding a You Are a Badass quote
4. Generating content
5. Saving and copying to clipboard

### Command-Line Modes

#### Generate Newsletter Only

```bash
python zabal.py newsletter --input "Today's events and reflections" --quote "You Are a Badass quote"
```

With file input:

```bash
python zabal.py newsletter --input daily_notes.txt --copy
```

#### Generate Social Content Only

From saved newsletter:

```bash
python zabal.py social --newsletter output/newsletters/newsletter_20260123.txt --link "https://newsletter.link" --copy
```

With video content:

```bash
python zabal.py social --newsletter newsletter.txt --video --copy
```

#### Generate Both (Full Workflow)

```bash
python zabal.py full --input "Daily reflection" --quote "Badass quote" --link "https://link" --copy
```

### Command Options

**Newsletter Command:**
- `--input, -i`: Daily input (text or file path)
- `--quote, -q`: You Are a Badass quote/reflection
- `--copy, -c`: Copy output to clipboard

**Social Command:**
- `--newsletter, -n`: Newsletter content (text or file path) [required]
- `--link, -l`: Newsletter link URL
- `--video, -v`: Include TikTok and YouTube content
- `--copy, -c`: Copy output to clipboard

**Full Command:**
- Combines all options from newsletter and social commands

## Output Structure

Generated content is automatically saved to:

```
output/
├── newsletters/
│   └── newsletter_YYYYMMDD.txt
└── social/
    └── social_YYYYMMDD.txt
```

## Daily Workflow Examples

### Quick Daily Post

```bash
# Interactive mode - easiest for daily use
python zabal.py

# Enter your thoughts when prompted
# Copy newsletter and social content to clipboard
# Paste into your platforms
```

### Scripted Workflow

```bash
# 1. Write daily notes in a file
echo "Today's reflection..." > today.txt

# 2. Generate everything
python zabal.py full -i today.txt -q "Badass quote" -l "https://newsletter.link" --copy

# 3. Social content is now in clipboard, ready to paste
```

### Two-Step Workflow

```bash
# 1. Generate and review newsletter first
python zabal.py newsletter -i today.txt

# 2. After publishing, generate social content
python zabal.py social -n output/newsletters/newsletter_20260123.txt -l "https://published-link" --copy
```

## Customization

### Modify Prompts

Edit the prompt files to adjust voice and formatting:

- `prompts/newsletter_prompt.txt` - Newsletter generation rules
- `prompts/social_prompt.txt` - Social content generation rules

### Change OpenAI Model

Edit `.env`:

```
OPENAI_MODEL=gpt-4o-mini  # For faster/cheaper generation
OPENAI_MODEL=gpt-4o       # For highest quality (default)
```

## Tips

1. **Interactive mode** is best for daily use - it guides you through everything
2. **CLI mode** is great for automation or when you have notes in files
3. Use `--copy` flag to automatically copy output to clipboard
4. All content is auto-saved with timestamps - you can always retrieve it later
5. The `full` command is perfect when you want to generate everything at once

## Troubleshooting

**"OpenAI API key not found"**
- Make sure `.env` file exists and contains `OPENAI_API_KEY=sk-...`

**"Module not found"**
- Run `pip install -r requirements.txt`

**Clipboard not working**
- Install clipboard support: `pip install pyperclip`
- On Linux, may need `xclip` or `xsel`: `sudo apt-get install xclip`

## Project Structure

```
ZABALNewsletterBot/
├── zabal.py                    # Main CLI interface
├── src/
│   ├── newsletter_generator.py # Newsletter generation logic
│   └── social_generator.py     # Social content generation logic
├── prompts/
│   ├── newsletter_prompt.txt   # Newsletter system prompt
│   └── social_prompt.txt       # Social content system prompt
├── output/                     # Generated content (auto-created)
│   ├── newsletters/
│   └── social/
├── requirements.txt
├── .env                        # Your API keys (create this)
├── .env.example               # Template
└── README.md
```

## License

Built for the ZABAL Team by BetterCallZaal.
