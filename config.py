import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    GOOGLE_SHEETS_CREDENTIALS_FILE = os.environ.get('GOOGLE_SHEETS_CREDENTIALS_FILE', 'aaiclas-web-feedback-d403f143c3d2.json')
    SPREADSHEET_NAME = os.environ.get('SPREADSHEET_NAME', 'aaiclas-web-feedback')