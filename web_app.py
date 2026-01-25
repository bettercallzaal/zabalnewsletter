#!/usr/bin/env python3
"""
ZABAL Newsletter Bot - Web Interface
Simple Flask app for generating newsletters and social content
"""

import os
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from src.newsletter_generator import NewsletterGenerator
from src.social_generator import SocialGenerator

load_dotenv()

app = Flask(__name__)

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
        
        if not daily_input:
            return jsonify({'error': 'Daily input is required'}), 400
        
        # Generate newsletter
        gen = NewsletterGenerator()
        newsletter = gen.generate(daily_input, badass_quote)
        filepath = gen.save_newsletter(newsletter)
        
        # Get day info
        day_num = gen.get_day_of_year()
        today = datetime.now()
        
        return jsonify({
            'success': True,
            'newsletter': newsletter,
            'filepath': filepath,
            'day_num': day_num,
            'date': today.strftime('%A, %B %d, %Y')
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
        social_content = gen.generate(newsletter_content, newsletter_link, has_video)
        filepath = gen.save_social_content(social_content)
        
        return jsonify({
            'success': True,
            'social_content': social_content,
            'filepath': filepath
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

if __name__ == '__main__':
    app.run(debug=True, port=5000)
