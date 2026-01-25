#!/usr/bin/env python3

import os
import sys
import argparse
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown
from rich import print as rprint
import pyperclip

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from newsletter_generator import NewsletterGenerator
from social_generator import SocialGenerator

console = Console()

def main():
    parser = argparse.ArgumentParser(
        description="ZABAL Newsletter & Social Content Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    newsletter_parser = subparsers.add_parser('newsletter', help='Generate newsletter')
    newsletter_parser.add_argument('--input', '-i', help='Daily input text or file path')
    newsletter_parser.add_argument('--quote', '-q', help='You Are a Badass quote/reflection')
    newsletter_parser.add_argument('--copy', '-c', action='store_true', help='Copy output to clipboard')
    
    social_parser = subparsers.add_parser('social', help='Generate social content')
    social_parser.add_argument('--newsletter', '-n', help='Newsletter content or file path', required=True)
    social_parser.add_argument('--link', '-l', help='Newsletter link URL')
    social_parser.add_argument('--video', '-v', action='store_true', help='Include video platforms (TikTok, YouTube)')
    social_parser.add_argument('--copy', '-c', action='store_true', help='Copy output to clipboard')
    
    full_parser = subparsers.add_parser('full', help='Generate both newsletter and social content')
    full_parser.add_argument('--input', '-i', help='Daily input text or file path')
    full_parser.add_argument('--quote', '-q', help='You Are a Badass quote/reflection')
    full_parser.add_argument('--link', '-l', help='Newsletter link URL')
    full_parser.add_argument('--video', '-v', action='store_true', help='Include video platforms (TikTok, YouTube)')
    full_parser.add_argument('--copy', '-c', action='store_true', help='Copy social content to clipboard')
    
    interactive_parser = subparsers.add_parser('interactive', help='Interactive mode (recommended)')
    
    args = parser.parse_args()
    
    if args.command == 'interactive' or args.command is None:
        run_interactive()
    elif args.command == 'newsletter':
        run_newsletter(args)
    elif args.command == 'social':
        run_social(args)
    elif args.command == 'full':
        run_full(args)

def run_interactive():
    console.print("\n[bold cyan]Year of the ZABAL - Content Generator[/bold cyan]\n")
    
    workflow = Prompt.ask(
        "What would you like to generate?",
        choices=["newsletter", "social", "both"],
        default="both"
    )
    
    if workflow in ["newsletter", "both"]:
        console.print("\n[bold]Newsletter Generation[/bold]")
        console.print("Enter your daily input (press Ctrl+D or Ctrl+Z when done):")
        
        daily_input_lines = []
        try:
            while True:
                line = input()
                daily_input_lines.append(line)
        except EOFError:
            pass
        
        daily_input = "\n".join(daily_input_lines)
        
        badass_quote = None
        if Confirm.ask("\nDo you have a You Are a Badass quote/reflection?"):
            console.print("Enter the quote (press Ctrl+D or Ctrl+Z when done):")
            quote_lines = []
            try:
                while True:
                    line = input()
                    quote_lines.append(line)
            except EOFError:
                pass
            badass_quote = "\n".join(quote_lines)
        
        console.print("\n[yellow]Generating newsletter...[/yellow]")
        
        gen = NewsletterGenerator()
        newsletter = gen.generate(daily_input, badass_quote)
        
        newsletter_path = gen.save_newsletter(newsletter)
        
        console.print(Panel(Markdown(newsletter), title="Newsletter Generated", border_style="green"))
        console.print(f"\n[green]✓[/green] Saved to: {newsletter_path}")
        
        if Confirm.ask("\nCopy newsletter to clipboard?"):
            pyperclip.copy(newsletter)
            console.print("[green]✓[/green] Copied to clipboard!")
    
    if workflow in ["social", "both"]:
        console.print("\n[bold]Social Content Generation[/bold]")
        
        if workflow == "social":
            newsletter_source = Prompt.ask(
                "Newsletter source",
                choices=["file", "paste"],
                default="file"
            )
            
            if newsletter_source == "file":
                newsletter_file = Prompt.ask("Enter newsletter file path")
                with open(newsletter_file, 'r') as f:
                    newsletter = f.read()
            else:
                console.print("Paste newsletter content (press Ctrl+D or Ctrl+Z when done):")
                newsletter_lines = []
                try:
                    while True:
                        line = input()
                        newsletter_lines.append(line)
                except EOFError:
                    pass
                newsletter = "\n".join(newsletter_lines)
        
        newsletter_link = None
        if Confirm.ask("\nDo you have a newsletter link?"):
            newsletter_link = Prompt.ask("Enter newsletter link")
        
        has_video = Confirm.ask("\nDoes this include video content?", default=False)
        
        console.print("\n[yellow]Generating social content...[/yellow]")
        
        social_gen = SocialGenerator()
        social_content = social_gen.generate(newsletter, newsletter_link, has_video)
        
        social_path = social_gen.save_social_content(social_content)
        
        console.print(Panel(Markdown(social_content), title="Social Content Generated", border_style="green"))
        console.print(f"\n[green]✓[/green] Saved to: {social_path}")
        
        if Confirm.ask("\nCopy social content to clipboard?"):
            pyperclip.copy(social_content)
            console.print("[green]✓[/green] Copied to clipboard!")
    
    console.print("\n[bold green]Done![/bold green]\n")

def run_newsletter(args):
    daily_input = read_input(args.input)
    badass_quote = args.quote
    
    console.print("\n[yellow]Generating newsletter...[/yellow]")
    
    gen = NewsletterGenerator()
    newsletter = gen.generate(daily_input, badass_quote)
    
    newsletter_path = gen.save_newsletter(newsletter)
    
    console.print(Panel(Markdown(newsletter), title="Newsletter Generated", border_style="green"))
    console.print(f"\n[green]✓[/green] Saved to: {newsletter_path}")
    
    if args.copy:
        pyperclip.copy(newsletter)
        console.print("[green]✓[/green] Copied to clipboard!")

def run_social(args):
    newsletter = read_input(args.newsletter)
    
    console.print("\n[yellow]Generating social content...[/yellow]")
    
    social_gen = SocialGenerator()
    social_content = social_gen.generate(newsletter, args.link, args.video)
    
    social_path = social_gen.save_social_content(social_content)
    
    console.print(Panel(Markdown(social_content), title="Social Content Generated", border_style="green"))
    console.print(f"\n[green]✓[/green] Saved to: {social_path}")
    
    if args.copy:
        pyperclip.copy(social_content)
        console.print("[green]✓[/green] Copied to clipboard!")

def run_full(args):
    daily_input = read_input(args.input)
    badass_quote = args.quote
    
    console.print("\n[yellow]Generating newsletter...[/yellow]")
    
    gen = NewsletterGenerator()
    newsletter = gen.generate(daily_input, badass_quote)
    
    newsletter_path = gen.save_newsletter(newsletter)
    
    console.print(Panel(Markdown(newsletter), title="Newsletter Generated", border_style="green"))
    console.print(f"\n[green]✓[/green] Saved to: {newsletter_path}")
    
    console.print("\n[yellow]Generating social content...[/yellow]")
    
    social_gen = SocialGenerator()
    social_content = social_gen.generate(newsletter, args.link, args.video)
    
    social_path = social_gen.save_social_content(social_content)
    
    console.print(Panel(Markdown(social_content), title="Social Content Generated", border_style="green"))
    console.print(f"\n[green]✓[/green] Saved to: {social_path}")
    
    if args.copy:
        pyperclip.copy(social_content)
        console.print("[green]✓[/green] Copied to clipboard!")
    
    console.print("\n[bold green]Done![/bold green]\n")

def read_input(input_arg):
    if input_arg is None:
        console.print("Enter input (press Ctrl+D or Ctrl+Z when done):")
        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            pass
        return "\n".join(lines)
    elif os.path.isfile(input_arg):
        with open(input_arg, 'r') as f:
            return f.read()
    else:
        return input_arg

if __name__ == "__main__":
    main()
