import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from pathlib import Path
from cleaner import clean_premier_league_table, clean_keeper_stats
from scraper import scrape_final_table, scrape_keeper_table
import logging
import os

# ✅ Logging setup
LOG_FILE = Path(__file__).parent / "upload.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()  # console output
    ]
)
logger = logging.getLogger(__name__)


def upload_to_google_sheets(
    df: pd.DataFrame,
    spreadsheet_name: str,
    worksheet_name: str,
    creds_path: str
) -> None:
    """Uploads DataFrame to Google Sheets with logging and error handling."""
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    try:
        creds_path = (Path(__file__).parent.parent / creds_path).resolve()
        logger.debug(f"Looking for credentials at: {creds_path}")

        if not creds_path.exists():
            raise FileNotFoundError(f"Credentials file not found at: {creds_path}")

        creds = Credentials.from_service_account_file(str(creds_path), scopes=scopes)
        client = gspread.authorize(creds)

        try:
            spreadsheet = client.open(spreadsheet_name)
        except gspread.SpreadsheetNotFound:
            logger.error(f"Spreadsheet '{spreadsheet_name}' not found.")
            return

        # Delete worksheet if it exists
        try:
            worksheet = spreadsheet.worksheet(worksheet_name)
            spreadsheet.del_worksheet(worksheet)
            logger.info(f"Deleted old worksheet: {worksheet_name}")
        except gspread.exceptions.WorksheetNotFound:
            logger.debug(f"Worksheet '{worksheet_name}' does not exist yet.")

        # Create new worksheet and upload data
        new_ws = spreadsheet.add_worksheet(
            title=worksheet_name,
            rows=str(max(len(df) + 1, 1)),
            cols=str(max(len(df.columns), 1)))

        data = [df.columns.tolist()] + df.fillna("").values.tolist()
        new_ws.update(range_name="A1", values=data)

        logger.info(f"Uploaded {len(df)} rows to worksheet '{worksheet_name}'")

    except Exception as e:
        logger.exception("Upload failed")


def get_data_path(filename: str) -> Path:
    """Get absolute path to data files."""
    return (Path(__file__).parent / filename).resolve()


if __name__ == "__main__":
    CREDS_PATH = "credentials/google_sheets_credentials.json"
    SPREADSHEET_NAME = "Premier League Data"
    STATS_FILE = "premier_league_stats.html"

    try:
        stats_path = get_data_path(STATS_FILE)

        logger.info("Processing league stats...")
        league_df = clean_premier_league_table(scrape_final_table(stats_path))
        upload_to_google_sheets(league_df, SPREADSHEET_NAME, "2024 Season", CREDS_PATH)

        logger.info("Processing goalkeeper stats...")
        gk_df = clean_keeper_stats(scrape_keeper_table(stats_path))
        upload_to_google_sheets(gk_df, SPREADSHEET_NAME, "2024 GK Stats", CREDS_PATH)

    except FileNotFoundError as e:
        logger.error(f"File error: {e}")
    except Exception as e:
        logger.exception("Unexpected error occurred")
