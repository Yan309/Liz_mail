"""Configuration management for the email automation system."""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration."""
    
    # SMTP Settings
    SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USER = os.getenv('SMTP_USER', '')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
    
    # Application Settings
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))
    EMAIL_BATCH_SIZE = int(os.getenv('EMAIL_BATCH_SIZE', 10))
    PROCESSING_DELAY = float(os.getenv('PROCESSING_DELAY', 2.0))
    
    # Upload Settings
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'zip'}
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    
    @staticmethod
    def validate():
        """Validate essential configuration."""
        if not Config.SMTP_USER or not Config.SMTP_PASSWORD:
            raise ValueError("SMTP credentials not configured. Please set SMTP_USER and SMTP_PASSWORD in .env file")
        return True
