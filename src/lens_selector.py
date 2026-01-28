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
    
    def select_lens(self, daily_input, override=None, roj_name=None):
        """
        Select appropriate lens based on day's content
        
        Args:
            daily_input: The day's reflection text
            override: Manual lens selection (overrides auto-selection)
            roj_name: Specific Roj day name for Zoroastrian calendar integration
        
        Returns:
            tuple: (lens_name, lens_data, reason, roj_guidance)
        """
        # Manual override
        if override and override != "auto" and override in self.lenses:
            logger.log_section("MINDFUL LENS SELECTION")
            logger.log("MODE", "manual override", "basic")
            logger.log("SELECTED LENS", override, "basic")
            
            # If override is zoroastrian_roj and roj_name provided, include specific Roj
            roj_guidance = None
            if override == "zoroastrian_roj" and roj_name:
                roj_calendar = self.lenses[override].get("roj_calendar", {})
                roj_guidance = roj_calendar.get(roj_name.lower(), None)
                if roj_guidance:
                    logger.log("ROJ", f"{roj_name}: {roj_guidance}", "basic")
            
            return override, self.lenses[override], "Manual override", roj_guidance
        
        if not daily_input:
            return "personal_observation", self.lenses.get("personal_observation", {}), "No input provided", None
        
        input_lower = daily_input.lower()
        
        # Check if Roj is mentioned in input
        roj_guidance = None
        if "roj:" in input_lower or "today is" in input_lower:
            # Try to detect which Roj is mentioned
            roj_calendar = self.lenses.get("zoroastrian_roj", {}).get("roj_calendar", {})
            for roj_key in roj_calendar.keys():
                if roj_key in input_lower:
                    roj_guidance = roj_calendar[roj_key]
                    if roj_name is None:
                        roj_name = roj_key
                    break
        
        # Check each lens's trigger words
        lens_scores = {}
        
        for lens_name, lens_data in self.lenses.items():
            if lens_name == "zoroastrian_roj":
                # Skip calendar check in auto-selection unless Roj explicitly mentioned
                continue
                
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
        
        # If Roj detected and no other strong matches, use zoroastrian_roj
        if roj_guidance and (not lens_scores or max(lens_scores.values(), key=lambda x: x["score"])["score"] < 2):
            lens_name = "zoroastrian_roj"
            reason = f"Roj observance detected: {roj_name}"
            
            if logger.is_enabled("log_prompt_assembly"):
                logger.log_section("MINDFUL LENS SELECTION")
                logger.log("SELECTED LENS", lens_name, "basic")
                logger.log("ROJ", f"{roj_name}: {roj_guidance}", "basic")
        
        # Select highest scoring lens
        elif lens_scores:
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
        
        return lens_name, self.lenses.get(lens_name, {}), reason, roj_guidance
    
    def get_lens_guidance(self, lens_name, roj_guidance=None):
        """Get guidance for a specific lens"""
        lens = self.lenses.get(lens_name, {})
        
        guidance_text = f"""
TONE: {lens.get('tone', '')}

GUIDANCE:
{chr(10).join('- ' + g for g in lens.get('guidance', []))}

AVOID:
{chr(10).join('- ' + a for a in lens.get('avoid', []))}
"""
        
        # Add Roj-specific guidance if provided
        if roj_guidance and lens_name == "zoroastrian_roj":
            guidance_text += f"\n\nTODAY'S ROJ OBSERVANCE:\n{roj_guidance}"
        
        return guidance_text.strip()
