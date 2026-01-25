import os
import json
from datetime import datetime

class MemoryManager:
    def __init__(self):
        self.memory_path = os.path.join(os.path.dirname(__file__), "..", "memory", "personality.json")
        self.ensure_memory_file()
    
    def ensure_memory_file(self):
        """Create memory file if it doesn't exist"""
        if not os.path.exists(self.memory_path):
            os.makedirs(os.path.dirname(self.memory_path), exist_ok=True)
            default_memory = {
                "voice_examples": [],
                "voice_donts": [],
                "style_notes": [],
                "context_memories": [],
                "current_projects": []
            }
            with open(self.memory_path, 'w') as f:
                json.dump(default_memory, f, indent=2)
    
    def load_memory(self):
        """Load personality memory"""
        try:
            with open(self.memory_path, 'r') as f:
                return json.load(f)
        except:
            return {
                "voice_examples": [],
                "voice_donts": [],
                "style_notes": [],
                "context_memories": [],
                "current_projects": []
            }
    
    def save_memory(self, memory_data):
        """Save personality memory"""
        try:
            with open(self.memory_path, 'w') as f:
                json.dump(memory_data, f, indent=2)
            return True
        except:
            return False
    
    def add_voice_example(self, title, content):
        """Add a voice example"""
        memory = self.load_memory()
        memory["voice_examples"].append({
            "title": title,
            "content": content,
            "added": datetime.now().isoformat()
        })
        return self.save_memory(memory)
    
    def add_style_note(self, note):
        """Add a style note"""
        memory = self.load_memory()
        if note not in memory["style_notes"]:
            memory["style_notes"].append(note)
        return self.save_memory(memory)
    
    def add_voice_dont(self, phrase):
        """Add a phrase to avoid"""
        memory = self.load_memory()
        if phrase not in memory["voice_donts"]:
            memory["voice_donts"].append(phrase)
        return self.save_memory(memory)
    
    def add_context_memory(self, memory_text):
        """Add context memory"""
        memory = self.load_memory()
        if memory_text not in memory["context_memories"]:
            memory["context_memories"].append(memory_text)
        return self.save_memory(memory)
    
    def get_enhanced_prompt(self, base_prompt):
        """Enhance prompt with personality memory"""
        memory = self.load_memory()
        
        enhanced = base_prompt + "\n\n"
        
        # Add voice examples
        if memory["voice_examples"]:
            enhanced += "=== VOICE EXAMPLES (Your Actual Writing) ===\n\n"
            for example in memory["voice_examples"]:
                enhanced += f"{example['title']}:\n{example['content']}\n\n"
        
        # Add voice don'ts
        if memory["voice_donts"]:
            enhanced += "=== NEVER USE THESE PHRASES ===\n"
            enhanced += "- " + "\n- ".join(memory["voice_donts"]) + "\n\n"
        
        # Add style notes
        if memory["style_notes"]:
            enhanced += "=== ADDITIONAL STYLE NOTES ===\n"
            enhanced += "- " + "\n- ".join(memory["style_notes"]) + "\n\n"
        
        # Add context
        if memory["context_memories"]:
            enhanced += "=== CONTEXT & BACKGROUND ===\n"
            enhanced += "- " + "\n- ".join(memory["context_memories"]) + "\n\n"
        
        # Add current projects
        if memory["current_projects"]:
            enhanced += "=== CURRENT PROJECTS ===\n"
            enhanced += "- " + "\n- ".join(memory["current_projects"]) + "\n\n"
        
        return enhanced
