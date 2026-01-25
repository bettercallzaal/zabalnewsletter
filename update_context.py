#!/usr/bin/env python3
"""
Interactive ZABAL Context Updater CLI
Run this to update personality.json from recent writing
"""

import sys
from src.context_updater import ZABALContextUpdater

def main():
    updater = ZABALContextUpdater()
    
    print("=" * 60)
    print("ZABAL CONTEXT UPDATER")
    print("=" * 60)
    print("\nThis tool updates memory/personality.json with evidence from")
    print("your recent writing to keep your AI voice consistent.\n")
    
    # Get sources
    print("Enter writing sources (URLs or paste text).")
    print("Type 'done' when finished, or 'cancel' to exit.\n")
    
    sources = []
    while True:
        source = input(f"Source {len(sources) + 1}: ").strip()
        if source.lower() == 'done':
            break
        if source.lower() == 'cancel':
            print("Cancelled.")
            return
        if source:
            sources.append(source)
    
    if not sources:
        print("No sources provided. Exiting.")
        return
    
    # Get optional feedback
    print("\nOptional: What felt 'off' in recent outputs?")
    print("(Press Enter to skip)")
    feedback = input("Feedback: ").strip() or None
    
    # Confirm
    print(f"\n📝 Will analyze {len(sources)} source(s)")
    if feedback:
        print(f"📝 With feedback: {feedback}")
    
    confirm = input("\nProceed? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("Cancelled.")
        return
    
    # Run update
    print("\n" + "=" * 60)
    result = updater.update_from_sources(sources, feedback, dry_run=False)
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        if "issues" in result:
            for issue in result["issues"]:
                print(f"  - {issue}")
        return
    
    # Display results
    print("\n" + "=" * 60)
    print("EDIT SUMMARY")
    print("=" * 60)
    for change in result["edit_summary"]:
        print(f"✓ {change}")
    
    print("\n" + "=" * 60)
    print("REASONING")
    print("=" * 60)
    print(result["reasoning"])
    
    print("\n" + "=" * 60)
    print("NEXT STEP")
    print("=" * 60)
    print(f"→ {result['next_step']}")
    
    if result.get("backup_path"):
        print(f"\n💾 Backup saved: {result['backup_path']}")
    
    print("\n✅ Context updated successfully!")

if __name__ == "__main__":
    main()
