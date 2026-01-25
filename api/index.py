"""
Vercel serverless entry point for ZABAL Newsletter Bot
"""
import sys
import os

# Add parent directory to path so we can import web_app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_app import app

# Vercel expects the Flask app to be named 'app'
# This file acts as the entry point for Vercel's serverless functions
