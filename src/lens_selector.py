"""
Mindful Lens Selector
Selects appropriate contemplative lens based on day's emotional tone
"""

import os
import json
from src.debug_logger import logger

class LensSelector:
    def __init__(self):
        self.lenses_path = os.path.join(
            os.path.dirname(__file__), 
            "..", 
            "memory", 
            "mindful_lenses.json"
        )
        self.lenses = self.load_lenses()
    
    def load_lenses(self):
        """Load mindful lenses registry"""
        try:
            with open(self.lenses_path, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def select_lens(self, daily_input, override=None):
        """
        Select appropriate lens based on day's content
        
        Args:
            daily_input: The day's reflection text
            override: Manual lens selection (overrides auto-selection)
        
        Returns:
            tuple: (lens_name, lens_data, reason)
        """
        # Manual override
        if override and override != "auto" and override in self.lenses:
            logger.log_section("MINDFUL LENS SELECTION")
            logger.log("MODE", "manual override", "basic")
            logger.log("SELECTED LENS", override, "basic")
            return override, self.lenses[override], "Manual override"
        
        if not daily_input:
            return "personal_observation", self.lenses.get("personal_observation", {}), "No input provided"
        
        input_lower = daily_input.lower()
        
        # Check each lens's trigger words
        lens_scores = {}
        
        for lens_name, lens_data in self.lenses.items():
            score = 0
            matched_triggers = []
            
            for trigger in lens_data.get("use_when", []):
                if trigger.lower() in input_lower:
                    score += 1
                    matched_triggers.append(trigger)
            
            if score > 0:
                lens_scores[lens_name] = {
                    "score": score,
                    "triggers": matched_triggers
                }
        
        # Select highest scoring lens
        if lens_scores:
            best_lens = max(lens_scores.items(), key=lambda x: x[1]["score"])
            lens_name = best_lens[0]
            triggers = best_lens[1]["triggers"]
            reason = f"Matched: {', '.join(triggers)}"
            
            if logger.is_enabled("log_prompt_assembly"):
                logger.log_section("MINDFUL LENS SELECTION")
                logger.log("SELECTED LENS", lens_name, "basic")
                logger.log("REASON", reason, "verbose")
                logger.log("TONE", self.lenses[lens_name].get("tone", ""), "verbose")
        else:
            # Default to personal observation if no triggers match
            lens_name = "personal_observation"
            reason = "No specific triggers - using personal observation"
            
            if logger.is_enabled("log_prompt_assembly"):
                logger.log("SELECTED LENS", f"{lens_name} (default)", "basic")
        
        return lens_name, self.lenses.get(lens_name, {}), reason
    
    def get_lens_guidance(self, lens_name):
        """Get guidance for a specific lens"""
        lens = self.lenses.get(lens_name, {})
        
        guidance_text = f"""
TONE: {lens.get('tone', '')}

GUIDANCE:
{chr(10).join('- ' + g for g in lens.get('guidance', []))}

AVOID:
{chr(10).join('- ' + a for a in lens.get('avoid', []))}
"""
        return guidance_text.strip()
