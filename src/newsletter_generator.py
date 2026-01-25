import os
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

class NewsletterGenerator:
    def __init__(self):
        use_ollama = os.getenv("USE_OLLAMA", "false").lower() == "true"
        use_claude = os.getenv("USE_CLAUDE", "false").lower() == "true"
        use_openrouter = os.getenv("USE_OPENROUTER", "false").lower() == "true"
        
        if use_ollama:
            # Ollama uses OpenAI-compatible API
            self.client = OpenAI(
                api_key="ollama",  # Ollama doesn't need a real API key
                base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
            )
            self.model = os.getenv("OLLAMA_MODEL", "llama3.2")
            self.provider = "openai"
        elif use_claude:
            if not ANTHROPIC_AVAILABLE:
                raise ImportError("Anthropic package not installed. Run: pip install anthropic")
            self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            self.model = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
            self.provider = "claude"
        elif use_openrouter:
            self.client = OpenAI(
                api_key=os.getenv("OPENROUTER_API_KEY"),
                base_url="https://openrouter.ai/api/v1"
            )
            self.model = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct:free")
            self.provider = "openai"
        else:
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            self.model = os.getenv("OPENAI_MODEL", "gpt-4o")
            self.provider = "openai"
        
        self.prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "newsletter_prompt.txt")
        
    def load_prompt(self):
        with open(self.prompt_path, 'r') as f:
            return f.read()
    
    def get_day_of_year(self):
        today = datetime.now()
        day_of_year = today.timetuple().tm_yday
        return day_of_year
    
    def generate(self, daily_input, badass_quote=None):
        system_prompt = self.load_prompt()
        
        today = datetime.now()
        day_num = self.get_day_of_year()
        date_str = today.strftime("%A, %B %d, %Y")
        
        user_message = f"Today is {date_str} (Day {day_num} of 2026).\n\n"
        user_message += f"Daily Input:\n{daily_input}\n\n"
        
        if badass_quote:
            user_message += f"You Are a Badass Quote/Reflection:\n{badass_quote}\n\n"
        
        user_message += "Generate today's Year of the ZABAL newsletter entry following the exact format and voice guidelines."
        
        if self.provider == "claude":
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
            )
            return response.content[0].text
        else:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
            )
            return response.choices[0].message.content
    
    def save_newsletter(self, content, filename=None):
        if filename is None:
            today = datetime.now()
            filename = f"newsletter_{today.strftime('%Y%m%d')}.txt"
        
        output_dir = os.path.join(os.path.dirname(__file__), "..", "output", "newsletters")
        os.makedirs(output_dir, exist_ok=True)
        
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w') as f:
            f.write(content)
        
        return filepath
