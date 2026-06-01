import os
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv()

class SheetsClient:
    def __init__(self):
        self.scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        creds_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH")
        if not creds_path or not os.path.exists(creds_path):
            raise Exception("Google Sheets credentials file not found. Please set GOOGLE_SHEETS_CREDENTIALS_PATH in .env")
        
        self.creds = Credentials.from_service_account_file(creds_path, scopes=self.scope)
        self.client = gspread.authorize(self.creds)
        self.sheet_name = os.getenv("SHEET_NAME", "aaiclas-web-feedback")
        self._init_sheet()

    def _init_sheet(self):
        """Find or create the worksheet and ensure headers exist"""
        try:
            self.sheet = self.client.open(self.sheet_name).sheet1
        except gspread.SpreadsheetNotFound:
            # Create new spreadsheet if not exists
            self.sheet = self.client.create(self.sheet_name).sheet1
            # Share with your email if needed (optional)
            # self.sheet.share('your-email@example.com', perm_type='user', role='writer')
        
        # Set headers if sheet is empty
        if not self.sheet.get_all_records():
            headers = [
                "TIMESTAMP", "AGENT", "COMPANY", "MOBILE",
                "EMAIL", "RATING", "FEEDBACK", "REMARKS"
            ]
            self.sheet.append_row(headers)

    def add_feedback(self, data):
        """Add a new feedback row to Google Sheets"""
        row = [
            data['timestamp'],
            data['agent_name'],
            data['company_name'],
            data['mobile_number'],
            data['email'],
            data['service_rating'],
            data['feedback'],
            data.get('remarks', '')
        ]
        self.sheet.append_row(row)
        return True