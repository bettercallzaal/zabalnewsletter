import os
from datetime import datetime
from openai import OpenAI

class SocialGenerator:
    def __init__(self):
        # Hardcoded Groq configuration - completely free
        self.client = OpenAI(
            api_key=os.getenv("GROQ_API_KEY", "gsk_demo_key_placeholder"),
            base_url="https://api.groq.com/openai/v1"
        )
        self.model = "llama-3.3-70b-versatile"
        self.provider = "groq"
        
        self.prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "social_prompt.txt")
        
    def load_prompt(self):
        with open(self.prompt_path, 'r') as f:
            return f.read()
    
    def generate_social_content(self, newsletter_content, newsletter_link=None, has_video=False):
        prompt_template = self.load_prompt()
        
        user_message = f"""Newsletter Content:
{newsletter_content}"""
        
        if newsletter_link:
            user_message += f"\n\nNewsletter Link: {newsletter_link}"
        
        if has_video:
            user_message += "\n\nNote: Video content available for TikTok/YouTube"
        
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
            
            social_content = response.choices[0].message.content
            
            # Save to file (skip in serverless environments like Vercel)
            filepath = None
            try:
                output_dir = os.path.join(os.path.dirname(__file__), "..", "output", "social")
                os.makedirs(output_dir, exist_ok=True)
                
                filename = f"social_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                filepath = os.path.join(output_dir, filename)
                
                with open(filepath, 'w') as f:
                    f.write(social_content)
            except (OSError, PermissionError):
                # Read-only filesystem (Vercel) - skip file saving
                filepath = "Not saved (serverless environment)"
            
            return {
                'social_content': social_content,
                'filepath': filepath or "Not saved"
            }
            
        except Exception as e:
            raise Exception(f"Error generating social content: {str(e)}")
