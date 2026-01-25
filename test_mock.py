#!/usr/bin/env python3

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from newsletter_generator import NewsletterGenerator
from social_generator import SocialGenerator

mock_newsletter = """Year of the ZABAL – Day 23 (Thursday, January 23, 2026)
Building the Infrastructure
___

Today was focused on building momentum with the ZABAL automation system. Spent the morning setting up the infrastructure for the newsletter bot - integrating OpenAI's API to handle both the daily reflections and social content generation. The goal is to streamline the entire workflow so creating content becomes effortless.

There's something clarifying about building tools that serve your own creative process. Not chasing features for the sake of it, just solving real friction points. The system is coming together piece by piece - newsletter generation, social posts for every platform, all from a single command.

Still need to integrate the Paragraph API for publishing, but that's next. For now, the foundation is solid.

The You Are a Badass calendar today reminded me: "Trust the process." Building systems takes time. Each piece matters. The automation isn't just about speed - it's about creating space for the work that actually matters. When the infrastructure handles the repetitive tasks, you're free to focus on the creative core.

Sometimes the best way forward is to build the tools that let you move faster tomorrow.

– BetterCallZaal on behalf of the ZABAL Team"""

print("=" * 80)
print("MOCK NEWSLETTER OUTPUT")
print("=" * 80)
print(mock_newsletter)
print("\n" + "=" * 80)

# Save it
gen = NewsletterGenerator()
newsletter_path = gen.save_newsletter(mock_newsletter, "test_newsletter.txt")
print(f"\n✓ Saved to: {newsletter_path}")

# Now test social generation
print("\n" + "=" * 80)
print("TESTING SOCIAL CONTENT GENERATION (This will use real API)")
print("=" * 80)

try:
    social_gen = SocialGenerator()
    social_content = social_gen.generate(mock_newsletter, "https://paragraph.com/@zabal/test-post", has_video=False)
    
    social_path = social_gen.save_social_content(social_content, "test_social.txt")
    
    print("\n" + "=" * 80)
    print("SOCIAL CONTENT OUTPUT")
    print("=" * 80)
    print(social_content)
    print("\n" + "=" * 80)
    print(f"\n✓ Saved to: {social_path}")
    
except Exception as e:
    print(f"\n✗ Error generating social content: {e}")
    print("\nThis is likely due to OpenAI API quota. Please check your billing at:")
    print("https://platform.openai.com/account/billing")
