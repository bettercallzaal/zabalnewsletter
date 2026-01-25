#!/usr/bin/env python3
"""
ZABAL Context Updater
Maintains personality.json with evidence-based updates from recent writing
"""

import os
import json
from datetime import datetime
from openai import OpenAI

class ZABALContextUpdater:
    def __init__(self):
        self.memory_path = os.path.join(os.path.dirname(__file__), "..", "memory", "personality.json")
        self.backup_dir = os.path.join(os.path.dirname(__file__), "..", "memory", "backups")
        
        # Groq client for analysis
        self.client = OpenAI(
            api_key=os.getenv("GROQ_API_KEY", "gsk_demo_key_placeholder"),
            base_url="https://api.groq.com/openai/v1"
        )
        self.model = "llama-3.3-70b-versatile"
        
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def backup_current_memory(self):
        """Create timestamped backup of current personality.json"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(self.backup_dir, f"personality_{timestamp}.json")
        
        with open(self.memory_path, 'r') as f:
            current = json.load(f)
        
        with open(backup_path, 'w') as f:
            json.dump(current, f, indent=2)
        
        return backup_path
    
    def load_current_memory(self):
        """Load current personality.json"""
        with open(self.memory_path, 'r') as f:
            return json.load(f)
    
    def save_memory(self, memory_data):
        """Save updated personality.json"""
        with open(self.memory_path, 'w') as f:
            json.dump(memory_data, f, indent=2)
    
    def analyze_writing_samples(self, sources, feedback=None):
        """
        Analyze writing samples and extract voice patterns
        
        Args:
            sources: List of URLs or text samples
            feedback: Optional feedback from Zaal about what felt off
        """
        
        current_memory = self.load_current_memory()
        
        # Build analysis prompt
        analysis_prompt = f"""You are the ZABAL Context Updater. Analyze the provided writing samples and current personality memory.

CURRENT MEMORY:
{json.dumps(current_memory, indent=2)}

WRITING SAMPLES TO ANALYZE:
{chr(10).join(sources)}

{f"ZAAL'S FEEDBACK: {feedback}" if feedback else ""}

TASK:
Extract voice patterns, identify what's working, and suggest minimal high-signal updates.

HARD RULES:
- NO marketing language
- NO motivational clichés
- NO contradictions with existing voice examples
- MINIMAL edits only (high signal)
- Evidence-based only

OUTPUT FORMAT (JSON):
{{
  "voice_patterns_found": ["pattern 1", "pattern 2", ...],
  "new_voice_examples": [
    {{"title": "...", "content": "...", "why": "..."}}
  ],
  "new_voice_donts": ["phrase 1", "phrase 2"],
  "new_style_notes": ["note 1", "note 2"],
  "context_updates": ["update 1", "update 2"],
  "current_state": {{
    "phase": "...",
    "energy": "...",
    "focus": ["...", "...", "..."],
    "avoid_this_week": ["...", "..."]
  }},
  "remove_weak_examples": [0, 2],
  "reasoning": "One paragraph explaining why these changes help"
}}

Be ruthless about quality. Only suggest additions that are unmistakably Zaal's voice."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a precise voice analyst. Extract patterns, never invent."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.3,
                max_tokens=3000
            )
            
            # Parse JSON response
            analysis = json.loads(response.choices[0].message.content)
            return analysis
            
        except Exception as e:
            print(f"Analysis failed: {e}")
            return None
    
    def apply_updates(self, analysis, current_memory):
        """Apply analyzed updates to memory with safety checks"""
        
        updated = current_memory.copy()
        changes = []
        
        # 1. Voice Examples (max 1-2 new, keep 5-12 total)
        if analysis.get("new_voice_examples"):
            # Remove weak examples first if specified
            if analysis.get("remove_weak_examples"):
                for idx in sorted(analysis["remove_weak_examples"], reverse=True):
                    if idx < len(updated["voice_examples"]):
                        removed = updated["voice_examples"].pop(idx)
                        changes.append(f"Removed weak example: {removed['title']}")
            
            # Add new examples (max 2)
            for example in analysis["new_voice_examples"][:2]:
                if len(updated["voice_examples"]) < 12:
                    updated["voice_examples"].append({
                        "title": example["title"],
                        "content": example["content"],
                        "added": datetime.now().isoformat()
                    })
                    changes.append(f"Added voice example: {example['title']}")
        
        # 2. Voice Don'ts (add only if not already present)
        if analysis.get("new_voice_donts"):
            for phrase in analysis["new_voice_donts"]:
                if phrase not in updated["voice_donts"]:
                    updated["voice_donts"].append(phrase)
                    changes.append(f"Added voice don't: {phrase}")
        
        # 3. Style Notes (add only if not already present)
        if analysis.get("new_style_notes"):
            for note in analysis["new_style_notes"]:
                if note not in updated["style_notes"]:
                    updated["style_notes"].append(note)
                    changes.append(f"Added style note: {note}")
        
        # 4. Context Updates
        if analysis.get("context_updates"):
            for update in analysis["context_updates"]:
                if update not in updated.get("context_memories", []):
                    if "context_memories" not in updated:
                        updated["context_memories"] = []
                    updated["context_memories"].append(update)
                    changes.append(f"Added context: {update}")
        
        # 5. Current State
        if analysis.get("current_state"):
            updated["current_state"] = analysis["current_state"]
            changes.append("Updated current state")
        
        return updated, changes
    
    def update_from_sources(self, sources, feedback=None, dry_run=False):
        """
        Main update workflow
        
        Args:
            sources: List of URLs or text samples
            feedback: Optional feedback from Zaal
            dry_run: If True, don't save changes
        
        Returns:
            dict with edit_summary, updated_json, and next_step
        """
        
        # 1. Backup current
        if not dry_run:
            backup_path = self.backup_current_memory()
            print(f"✅ Backed up to: {backup_path}")
        
        # 2. Load current
        current_memory = self.load_current_memory()
        
        # 3. Analyze sources
        print("🔍 Analyzing writing samples...")
        analysis = self.analyze_writing_samples(sources, feedback)
        
        if not analysis:
            return {"error": "Analysis failed"}
        
        # 4. Apply updates with safety checks
        updated_memory, changes = self.apply_updates(analysis, current_memory)
        
        # 5. Safety checks
        safety_issues = []
        
        # Check: Did we add too many examples?
        if len(updated_memory.get("voice_examples", [])) > 12:
            safety_issues.append("Too many voice examples (>12)")
        
        # Check: Did we add marketing language?
        marketing_words = ["leverage", "synergy", "disrupt", "revolutionary", "game-changing"]
        for example in updated_memory.get("voice_examples", []):
            if any(word in example["content"].lower() for word in marketing_words):
                safety_issues.append(f"Marketing language detected in: {example['title']}")
        
        if safety_issues:
            print("⚠️  Safety issues detected:")
            for issue in safety_issues:
                print(f"  - {issue}")
            if not dry_run:
                return {"error": "Safety checks failed", "issues": safety_issues}
        
        # 6. Save if not dry run
        if not dry_run:
            self.save_memory(updated_memory)
            print("✅ Memory updated successfully")
        
        # 7. Generate output
        return {
            "edit_summary": changes,
            "updated_json": updated_memory,
            "reasoning": analysis.get("reasoning", ""),
            "next_step": "Generate a test newsletter to verify voice consistency",
            "backup_path": backup_path if not dry_run else None
        }


if __name__ == "__main__":
    updater = ZABALContextUpdater()
    
    # Example usage
    print("ZABAL Context Updater")
    print("=" * 50)
    print("\nUsage:")
    print("  python src/context_updater.py")
    print("\nOr import and use programmatically:")
    print("  from src.context_updater import ZABALContextUpdater")
    print("  updater = ZABALContextUpdater()")
    print("  result = updater.update_from_sources(sources, feedback)")
