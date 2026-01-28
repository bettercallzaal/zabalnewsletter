import os
import json
from datetime import datetime
from src.debug_logger import logger
from src.lens_selector import LensSelector

class MemoryManager:
    def __init__(self):
        self.memory_path = os.path.join(os.path.dirname(__file__), "..", "memory", "personality.json")
        self.lens_selector = LensSelector()
        self.budget_path = os.path.join(os.path.dirname(__file__), "..", "config", "prompt_budget.json")
        self.load_budget()
        self.ensure_memory_file()
    
    def load_budget(self):
        """Load prompt budget configuration"""
        try:
            with open(self.budget_path, 'r') as f:
                self.budget = json.load(f)
        except:
            # Default budget if file doesn't exist
            self.budget = {
                "target_chars": 10000,
                "hard_limit": 12000,
                "prune_order": ["voice_examples", "style_notes", "context_memories"]
            }
    
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
        if logger.is_enabled("log_memory_injection"):
            logger.log_section("MEMORY INJECTION START")
        
        memory = self.load_memory()
        
        enhanced = base_prompt + "\n\n"
        
        # Add voice examples
        if memory["voice_examples"]:
            logger.log("VOICE EXAMPLES ADDED", 
                      f"{len(memory['voice_examples'])} examples", 
                      "verbose")
            for example in memory["voice_examples"]:
                logger.log(f"  - {example['title']}", 
                          f"{len(example['content'])} chars", 
                          "trace")
            
            enhanced += "=== VOICE EXAMPLES (Your Actual Writing) ===\n\n"
            for example in memory["voice_examples"]:
                enhanced += f"{example['title']}:\n{example['content']}\n\n"
        
        # Add voice don'ts
        if memory["voice_donts"]:
            logger.log("VOICE DONTS ADDED", 
                      f"{len(memory['voice_donts'])} phrases", 
                      "verbose")
            logger.log("  Phrases", memory["voice_donts"], "trace")
            
            enhanced += "=== NEVER USE THESE PHRASES ===\n"
            enhanced += "- " + "\n- ".join(memory["voice_donts"]) + "\n\n"
        
        # Add style notes
        if memory["style_notes"]:
            logger.log("STYLE NOTES ADDED", 
                      f"{len(memory['style_notes'])} notes", 
                      "verbose")
            logger.log("  Notes", memory["style_notes"], "trace")
            
            enhanced += "=== ADDITIONAL STYLE NOTES ===\n"
            enhanced += "- " + "\n- ".join(memory["style_notes"]) + "\n\n"
        
        # Add context
        if memory["context_memories"]:
            logger.log("CONTEXT MEMORIES ADDED", 
                      f"{len(memory['context_memories'])} items", 
                      "verbose")
            
            enhanced += "=== CONTEXT & BACKGROUND ===\n"
            enhanced += "- " + "\n- ".join(memory["context_memories"]) + "\n\n"
        
        # Add current projects
        if memory["current_projects"]:
            logger.log("CURRENT PROJECTS ADDED", 
                      f"{len(memory['current_projects'])} projects", 
                      "verbose")
            
            enhanced += "=== CURRENT PROJECTS ===\n"
            enhanced += "- " + "\n- ".join(memory["current_projects"]) + "\n\n"
        
        if logger.is_enabled("log_memory_injection"):
            logger.log("MEMORY SUMMARY", 
                      f"{len(memory.get('voice_examples', []))} examples, "
                      f"{len(memory.get('voice_donts', []))} donts, "
                      f"{len(memory.get('style_notes', []))} style rules",
                      "basic")
        
        # Check prompt budget
        enhanced = self._check_budget(enhanced, memory)
        
        return enhanced
    
    def _check_budget(self, prompt, memory):
        """Check and enforce prompt budget"""
        prompt_length = len(prompt)
        target = self.budget.get("target_chars", 10000)
        hard_limit = self.budget.get("hard_limit", 12000)
        
        if prompt_length <= target:
            return prompt
        
        if prompt_length > hard_limit:
            logger.log_section("PROMPT BUDGET - HARD LIMIT EXCEEDED")
            logger.log("TARGET", f"{target} chars", "basic", force=True)
            logger.log("ACTUAL", f"{prompt_length} chars", "basic", force=True)
            logger.log("ACTION", "Auto-pruning required", "basic", force=True)
            
            # Auto-prune
            return self._auto_prune(prompt, memory, target)
        
        else:
            # Warning only
            logger.log("PROMPT BUDGET WARNING", 
                      f"{prompt_length} chars (target: {target}, limit: {hard_limit})",
                      "basic")
            return prompt
    
    def _auto_prune(self, prompt, memory, target):
        """Auto-prune memory to fit budget"""
        prune_order = self.budget.get("prune_order", ["voice_examples"])
        
        for category in prune_order:
            if category == "voice_examples" and len(memory.get("voice_examples", [])) > 3:
                # Remove oldest example
                removed = memory["voice_examples"].pop(0)
                logger.log("PRUNED", f"Removed voice example: {removed.get('title', 'Unknown')}", "basic", force=True)
                
                # Save pruned memory
                self.save_memory(memory)
                
                # Regenerate prompt
                return self.get_enhanced_prompt(prompt.split("\n\n")[0])  # Rebuild from base
            
            elif category == "style_notes" and len(memory.get("style_notes", [])) > 5:
                # Remove last style note
                removed = memory["style_notes"].pop()
                logger.log("PRUNED", f"Removed style note: {removed[:50]}...", "basic", force=True)
                self.save_memory(memory)
                return self.get_enhanced_prompt(prompt.split("\n\n")[0])
        
        # If still over budget, just warn
        logger.log("PRUNE WARNING", "Could not prune enough - manual review needed", "basic", force=True)
        return prompt
    
    def get_enhanced_prompt_with_lens(self, base_prompt, daily_input, lens_override=None, roj_context=None, editing_instructions=None, parameters=None):
        """
        Get enhanced prompt with lens-specific guidance and voice parameters
        
        Args:
            base_prompt: Base newsletter prompt
            daily_input: The day's reflection (for lens selection)
            lens_override: Manual lens selection (optional)
            roj_context: Full Roj observance text for Zoroastrian calendar (optional)
            editing_instructions: Natural language editing instructions from user (optional)
            parameters: Generation parameters including voice controls (optional)
        
        Returns:
            Enhanced prompt with lens guidance and parameter instructions
        """
        # Get base enhancement
        enhanced = self.get_enhanced_prompt(base_prompt)
        
        # Select and add lens guidance (with optional override and roj support)
        lens_name, lens_data, reason, roj_guidance = self.lens_selector.select_lens(daily_input, override=lens_override, roj_name=None)
        
        if lens_data:
            lens_guidance = self.lens_selector.get_lens_guidance(lens_name, roj_guidance=roj_guidance)
            enhanced += f"\n\n=== MINDFUL LENS FOR TODAY ===\n{lens_guidance}\n\n"
            
            if logger.is_enabled("log_prompt_assembly"):
                logger.log("LENS ADDED", f"{lens_name} - {reason}", "basic")
        
        # Add Roj context if provided (for Zoroastrian observances)
        if roj_context and lens_name == "zoroastrian_roj":
            enhanced += f"\n\n=== ROJ OBSERVANCE FOR TODAY ===\n{roj_context}\n\nUse this Roj teaching as the foundation for the mindful moment. Reference it directly and connect it to what happened today.\n\n"
            
            if logger.is_enabled("log_prompt_assembly"):
                logger.log("ROJ CONTEXT", f"Added {len(roj_context)} chars", "basic")
        
        # Add editing instructions if provided
        if editing_instructions:
            enhanced += f"\n\n=== EDITING INSTRUCTIONS ===\nThe user has provided specific editing guidance:\n\n{editing_instructions}\n\nApply these instructions to the newsletter output. Follow them precisely while maintaining the overall voice and structure.\n\n"
            
            if logger.is_enabled("log_prompt_assembly"):
                logger.log("EDITING INSTRUCTIONS", editing_instructions[:100], "basic")
        
        # Add voice parameter guidance if provided
        if parameters:
            voice_params = self._build_voice_guidance(parameters)
            if voice_params:
                enhanced += f"\n\n=== VOICE PARAMETERS ===\n{voice_params}\n\n"
                
                if logger.is_enabled("log_prompt_assembly"):
                    logger.log("VOICE PARAMS", f"Formality: {parameters.get('formality')}, Energy: {parameters.get('energy_level')}", "basic")
        
        return enhanced
    
    def _build_voice_guidance(self, parameters):
        """Build voice parameter guidance text"""
        guidance_parts = []
        
        # Formality
        formality = parameters.get('formality', 5)
        if formality <= 3:
            guidance_parts.append("FORMALITY: Very casual, conversational tone. Use contractions, informal language.")
        elif formality >= 7:
            guidance_parts.append("FORMALITY: More formal, polished tone. Avoid slang, use complete sentences.")
        else:
            guidance_parts.append("FORMALITY: Balanced tone - natural but not overly casual.")
        
        # Energy Level
        energy = parameters.get('energy_level', 5)
        if energy <= 3:
            guidance_parts.append("ENERGY: Subdued, quiet, contemplative. Gentle pacing, soft observations.")
        elif energy >= 7:
            guidance_parts.append("ENERGY: Energetic, dynamic. More momentum, active language.")
        else:
            guidance_parts.append("ENERGY: Steady, grounded. Neither rushed nor slow.")
        
        # Reflection Depth
        depth = parameters.get('reflection_depth', 5)
        if depth <= 3:
            guidance_parts.append("DEPTH: Surface-level observations. What happened, what was noticed.")
        elif depth >= 7:
            guidance_parts.append("DEPTH: Deeper philosophical reflection. Patterns, meaning, broader implications.")
        else:
            guidance_parts.append("DEPTH: Moderate reflection. Some insight without over-analyzing.")
        
        # Personal vs Universal
        scope = parameters.get('personal_universal', 5)
        if scope <= 3:
            guidance_parts.append("SCOPE: Very personal, intimate. Specific to this day, this experience.")
        elif scope >= 7:
            guidance_parts.append("SCOPE: Broadly relatable. Universal themes that others can connect to.")
        else:
            guidance_parts.append("SCOPE: Balanced - personal but accessible.")
        
        return "\n".join(guidance_parts)
