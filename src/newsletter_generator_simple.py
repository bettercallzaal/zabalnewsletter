import os
from datetime import datetime
from openai import OpenAI

class NewsletterGenerator:
    def __init__(self):
        # Hardcoded Groq configuration - completely free, no API key needed for basic use
        # Using Groq's free tier: 1000 requests/day, 6000 tokens/minute
        self.client = OpenAI(
            api_key=os.getenv("GROQ_API_KEY", "gsk_demo_key_placeholder"),  # Will use env var or placeholder
            base_url="https://api.groq.com/openai/v1"
        )
        # Using Llama 3.3 70B - excellent quality, completely free
        self.model = "llama-3.3-70b-versatile"
        self.provider = "groq"
        
        self.prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "newsletter_prompt.txt")
        
    def load_prompt(self):
        with open(self.prompt_path, 'r') as f:
            return f.read()
    
    def calculate_day_number(self):
        start_date = datetime(2025, 1, 1)
        today = datetime.now()
        delta = today - start_date
        return delta.days + 1
    
    def generate_newsletter(self, daily_input, badass_quote=None):
        day_num = self.calculate_day_number()
        today_str = datetime.now().strftime('%B %d, %Y')
        
        prompt_template = self.load_prompt()
        
        user_message = f"""Day {day_num} - {today_str}

Daily Input:
{daily_input}"""
        
        if badass_quote:
            user_message += f"\n\nYou Are a Badass Quote:\n{badass_quote}"
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": prompt_template},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            newsletter = response.choices[0].message.content
            
            # Save to file (skip in serverless environments like Vercel)
            filepath = None
            try:
                output_dir = os.path.join(os.path.dirname(__file__), "..", "output", "newsletters")
                os.makedirs(output_dir, exist_ok=True)
                
                filename = f"newsletter_day_{day_num}_{datetime.now().strftime('%Y%m%d')}.txt"
                filepath = os.path.join(output_dir, filename)
                
                with open(filepath, 'w') as f:
                    f.write(newsletter)
            except (OSError, PermissionError):
                # Read-only filesystem (Vercel) - skip file saving
                filepath = "Not saved (serverless environment)"
            
            return {
                'newsletter': newsletter,
                'day_num': day_num,
                'date': today_str,
                'filepath': filepath or "Not saved"
            }
            
        except Exception as e:
            raise Exception(f"Error generating newsletter: {str(e)}")
