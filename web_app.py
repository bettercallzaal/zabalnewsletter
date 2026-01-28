#!/usr/bin/env python3
"""
ZABAL Newsletter Bot - Web Interface
Simple Flask app for generating newsletters and social content
"""

import os
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from src.newsletter_generator_simple import NewsletterGenerator
from src.social_generator_simple import SocialGenerator
from src.memory_manager import MemoryManager

load_dotenv()

app = Flask(__name__)
memory_manager = MemoryManager()

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/generate/newsletter', methods=['POST'])
def generate_newsletter():
    """Generate newsletter from daily input"""
    try:
        data = request.json
        daily_input = data.get('daily_input', '')
        badass_quote = data.get('badass_quote', '')
        lens_override = data.get('lens_override', None)
        roj_context = data.get('roj_context', '')
        editing_instructions = data.get('editing_instructions', '')
        parameters = data.get('parameters', None)
        
        if not daily_input:
            return jsonify({'error': 'Daily input is required'}), 400
        
        # Generate newsletter (with optional lens override and parameters)
        gen = NewsletterGenerator()
        result = gen.generate_newsletter(daily_input, badass_quote, lens_override, roj_context, editing_instructions, parameters)
        
        return jsonify({
            'success': True,
            'newsletter': result['newsletter'],
            'filepath': result['filepath'],
            'day_num': result['day_num'],
            'date': result['date']
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate/social', methods=['POST'])
def generate_social():
    """Generate social content from newsletter"""
    try:
        data = request.json
        newsletter_content = data.get('newsletter_content', '')
        newsletter_link = data.get('newsletter_link', '')
        has_video = data.get('has_video', False)
        
        if not newsletter_content:
            return jsonify({'error': 'Newsletter content is required'}), 400
        
        # Generate social content
        gen = SocialGenerator()
        result = gen.generate_social_content(newsletter_content, newsletter_link, has_video)
        
        return jsonify({
            'success': True,
            'social_content': result['social_content'],
            'filepath': result['filepath']
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/history/newsletters')
def list_newsletters():
    """List all saved newsletters"""
    try:
        output_dir = os.path.join(os.path.dirname(__file__), "output", "newsletters")
        if not os.path.exists(output_dir):
            return jsonify({'newsletters': []})
        
        files = []
        for filename in sorted(os.listdir(output_dir), reverse=True):
            if filename.endswith('.txt'):
                filepath = os.path.join(output_dir, filename)
                with open(filepath, 'r') as f:
                    content = f.read()
                    # Extract title (first line)
                    title = content.split('\n')[0] if content else filename
                files.append({
                    'filename': filename,
                    'title': title,
                    'path': filepath
                })
        
        return jsonify({'newsletters': files})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/history/newsletter/<filename>')
def get_newsletter(filename):
    """Get specific newsletter content"""
    try:
        output_dir = os.path.join(os.path.dirname(__file__), "output", "newsletters")
        filepath = os.path.join(output_dir, filename)
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'Newsletter not found'}), 404
        
        with open(filepath, 'r') as f:
            content = f.read()
        
        return jsonify({
            'success': True,
            'content': content,
            'filename': filename
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/prompts/get/<prompt_type>')
def get_prompt(prompt_type):
    """Get current prompt content"""
    try:
        if prompt_type not in ['newsletter', 'social']:
            return jsonify({'error': 'Invalid prompt type'}), 400
        
        prompt_path = os.path.join(os.path.dirname(__file__), "prompts", f"{prompt_type}_prompt.txt")
        
        if not os.path.exists(prompt_path):
            return jsonify({'error': 'Prompt file not found'}), 404
        
        with open(prompt_path, 'r') as f:
            content = f.read()
        
        return jsonify({
            'success': True,
            'content': content,
            'type': prompt_type
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/prompts/improve', methods=['POST'])
def improve_prompt():
    """Use LLM to improve prompt based on feedback"""
    try:
        data = request.json
        prompt_type = data.get('prompt_type', '')
        current_prompt = data.get('current_prompt', '')
        feedback = data.get('feedback', '')
        
        if not all([prompt_type, current_prompt, feedback]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Use the same LLM to improve the prompt
        gen = NewsletterGenerator()
        
        improvement_request = f"""You are a prompt engineering expert. Your task is to improve the following prompt based on user feedback.

CURRENT PROMPT:
{current_prompt}

USER FEEDBACK:
{feedback}

Please provide an improved version of the prompt that incorporates the user's feedback while maintaining the original structure and intent. Return ONLY the improved prompt text, no explanations."""

        if gen.provider == "claude":
            response = gen.client.messages.create(
                model=gen.model,
                max_tokens=4096,
                messages=[
                    {"role": "user", "content": improvement_request}
                ],
                temperature=0.7,
            )
            improved_prompt = response.content[0].text
        else:
            response = gen.client.chat.completions.create(
                model=gen.model,
                messages=[
                    {"role": "user", "content": improvement_request}
                ],
                temperature=0.7,
            )
            improved_prompt = response.choices[0].message.content
        
        return jsonify({
            'success': True,
            'improved_prompt': improved_prompt
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/prompts/save', methods=['POST'])
def save_prompt():
    """Save updated prompt to file"""
    try:
        data = request.json
        prompt_type = data.get('prompt_type', '')
        content = data.get('content', '')
        
        if not all([prompt_type, content]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        if prompt_type not in ['newsletter', 'social']:
            return jsonify({'error': 'Invalid prompt type'}), 400
        
        # Backup current prompt
        prompt_path = os.path.join(os.path.dirname(__file__), "prompts", f"{prompt_type}_prompt.txt")
        backup_dir = os.path.join(os.path.dirname(__file__), "prompts", "backups")
        os.makedirs(backup_dir, exist_ok=True)
        
        if os.path.exists(prompt_path):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = os.path.join(backup_dir, f"{prompt_type}_prompt_{timestamp}.txt")
            with open(prompt_path, 'r') as f:
                backup_content = f.read()
            with open(backup_path, 'w') as f:
                f.write(backup_content)
        
        # Save new prompt
        with open(prompt_path, 'w') as f:
            f.write(content)
        
        return jsonify({
            'success': True,
            'message': 'Prompt saved successfully',
            'backup_created': True
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/memory/get')
def get_memory():
    """Get all personality memory"""
    try:
        memory = memory_manager.load_memory()
        return jsonify({
            'success': True,
            'memory': memory
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/memory/add', methods=['POST'])
def add_memory():
    """Add memory item"""
    try:
        data = request.json
        memory_type = data.get('type', '')
        content = data.get('content', '')
        
        if memory_type == 'voice_example':
            title = data.get('title', '')
            memory_manager.add_voice_example(title, content)
        elif memory_type == 'style_note':
            memory_manager.add_style_note(content)
        elif memory_type == 'voice_dont':
            memory_manager.add_voice_dont(content)
        elif memory_type == 'context':
            memory_manager.add_context_memory(content)
        else:
            return jsonify({'error': 'Invalid memory type'}), 400
        
        return jsonify({
            'success': True,
            'message': 'Memory added successfully'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/memory/update', methods=['POST'])
def update_memory():
    """Update entire memory"""
    try:
        data = request.json
        memory_data = data.get('memory', {})
        
        if memory_manager.save_memory(memory_data):
            return jsonify({
                'success': True,
                'message': 'Memory updated successfully'
            })
        else:
            return jsonify({'error': 'Failed to save memory'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
