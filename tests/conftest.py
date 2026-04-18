"""
Pytest conftest.py - Add backend and whatsapp-assistant to sys.path
so that tests can import modules the same way the app does internally.
"""
import sys
import os

# Add backend directory so that 'from api.x' / 'from utils.x' / 'from scrapers.x' works
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Add whatsapp-assistant directory so that 'from config import' / 'from handlers.x' works
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'whatsapp-assistant'))
