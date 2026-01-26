"""
Constitution Checker - Enforces editorial rules post-generation
Validates output against ZABAL editorial constitution
"""

import re
import json
import os
from src.debug_logger import logger

class ConstitutionChecker:
    def __init__(self, rules_path=None):
        if rules_path is None:
            rules_path = os.path.join(
                os.path.dirname(__file__),
                "..",
                "memory",
                "editorial_rules.json"
            )
        
        with open(rules_path, 'r') as f:
            self.rules = json.load(f)
    
    def check(self, text, content_type="newsletter"):
        """
        Check output against editorial rules
        
        Args:
            text: Generated content
            content_type: "newsletter" or "social"
        
        Returns:
            list of issues found
        """
        issues = []
        
        # Check hard bans
        bans = self.rules.get("hard_bans", [])
        for phrase in bans:
            if phrase.lower() in text.lower():
                issues.append(f"BANNED_PHRASE: {phrase}")
        
        # Content-specific checks
        if content_type == "newsletter":
            issues.extend(self._check_newsletter(text))
        elif content_type == "social":
            issues.extend(self._check_social(text))
        
        # Log results
        if logger.is_enabled("log_prompt_assembly"):
            if issues:
                logger.log_section("CONSTITUTION CHECK - ISSUES FOUND")
                for issue in issues:
                    logger.log("ISSUE", issue, "basic")
            else:
                logger.log("CONSTITUTION CHECK", "✓ All rules passed", "basic")
        
        return issues
    
    def _check_newsletter(self, text):
        """Newsletter-specific checks"""
        issues = []
        constraints = self.rules.get("output_constraints", {}).get("newsletter", {})
        
        # Check signature
        if constraints.get("require_signature"):
            if "– BetterCallZaal on behalf of the ZABAL Team" not in text:
                issues.append("MISSING_SIGNATURE")
        
        # Check closing line length (find last non-signature line)
        lines = text.strip().split("\n")
        closing_line = None
        for i in range(len(lines) - 1, -1, -1):
            if lines[i].strip() and "BetterCallZaal" not in lines[i]:
                closing_line = lines[i].strip()
                break
        
        if closing_line:
            sentence_count = len([s for s in closing_line.split(".") if s.strip()])
            max_sentences = constraints.get("closing_line_max_sentences", 1)
            
            if sentence_count > max_sentences:
                issues.append(f"CLOSING_TOO_LONG: {sentence_count} sentences (max {max_sentences})")
        
        # Check for multiple lens mixing (heuristic)
        lens_indicators = {
            "you are a badass": 0,
            "don't sweat": 0,
            "stoic": 0,
            "zen": 0,
            "buddha": 0,
            "marcus aurelius": 0
        }
        
        text_lower = text.lower()
        for indicator in lens_indicators:
            if indicator in text_lower:
                lens_indicators[indicator] = 1
        
        if sum(lens_indicators.values()) > 1:
            issues.append("MULTIPLE_LENSES_DETECTED")
        
        return issues
    
    def _check_social(self, text):
        """Social content-specific checks"""
        issues = []
        constraints = self.rules.get("output_constraints", {}).get("social", {})
        
        # Check ZM prefix
        if constraints.get("require_ZM_prefix"):
            if not text.strip().upper().startswith("ZM"):
                issues.append("MISSING_ZM_PREFIX")
        
        # Check for emojis or hashtags
        if constraints.get("no_emojis") or constraints.get("no_hashtags"):
            emoji_pattern = re.compile(
                r"[\U0001F300-\U0001FAFF]|#",
                flags=re.UNICODE
            )
            if emoji_pattern.search(text):
                issues.append("EMOJI_OR_HASHTAG_FOUND")
        
        return issues
    
    def auto_fix(self, text, issues, content_type="newsletter"):
        """
        Attempt to auto-fix safe issues
        
        Args:
            text: Original text
            issues: List of issues from check()
            content_type: "newsletter" or "social"
        
        Returns:
            tuple: (fixed_text, remaining_issues)
        """
        fixed = text
        remaining = []
        
        for issue in issues:
            if issue == "MISSING_SIGNATURE":
                # Auto-fix: add signature
                fixed = fixed.rstrip() + "\n\n– BetterCallZaal on behalf of the ZABAL Team"
                logger.log("AUTO-FIX", "Added missing signature", "basic")
            
            elif issue.startswith("CLOSING_TOO_LONG"):
                # Auto-fix: trim to first sentence (find last non-signature line)
                lines = fixed.strip().split("\n")
                for i in range(len(lines) - 1, -1, -1):
                    if lines[i].strip() and "BetterCallZaal" not in lines[i]:
                        closing = lines[i]
                        first_sentence = closing.split(".")[0] + "."
                        lines[i] = first_sentence
                        fixed = "\n".join(lines)
                        logger.log("AUTO-FIX", "Trimmed closing line to 1 sentence", "basic")
                        break
            
            elif issue == "MISSING_ZM_PREFIX":
                # Auto-fix: add ZM prefix
                fixed = "ZM " + fixed.lstrip()
                logger.log("AUTO-FIX", "Added ZM prefix", "basic")
            
            elif issue.startswith("BANNED_PHRASE"):
                # Cannot auto-fix - needs regeneration
                remaining.append(issue)
                logger.log("CANNOT AUTO-FIX", issue, "basic")
            
            elif issue == "MULTIPLE_LENSES_DETECTED":
                # Cannot auto-fix - needs regeneration
                remaining.append(issue)
                logger.log("CANNOT AUTO-FIX", issue, "basic")
            
            else:
                remaining.append(issue)
        
        return fixed, remaining


def validate_output(text, content_type="newsletter", auto_fix_enabled=True):
    """
    Convenience function to check and optionally fix output
    
    Args:
        text: Generated content
        content_type: "newsletter" or "social"
        auto_fix_enabled: Whether to attempt auto-fixes
    
    Returns:
        tuple: (validated_text, issues_found, was_fixed)
    """
    checker = ConstitutionChecker()
    issues = checker.check(text, content_type)
    
    if not issues:
        return text, [], False
    
    if auto_fix_enabled:
        fixed_text, remaining_issues = checker.auto_fix(text, issues, content_type)
        was_fixed = len(remaining_issues) < len(issues)
        return fixed_text, remaining_issues, was_fixed
    
    return text, issues, False
