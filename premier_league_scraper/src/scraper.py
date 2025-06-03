import os
from bs4 import BeautifulSoup, Comment
import pandas as pd
from pathlib import Path

def extract_table_from_html(soup: BeautifulSoup, table_id: str):
    # Some sports websites (like FBref) wrap tables in comments
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))
    for comment in comments:
        comment_soup = BeautifulSoup(comment, "html.parser")
        table = comment_soup.find("table", id=table_id)
        if table:
            return table

    # Fallback if table isn't in comments
    return soup.find("table", id=table_id)

def scrape_table_by_id(html_file_name: str, table_id: str) -> pd.DataFrame:
    """Scrape a table from HTML file by table ID"""
    file_path = Path(__file__).parent / html_file_name
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")
    except FileNotFoundError:
        raise FileNotFoundError(f"HTML file not found at: {file_path}")

    table = extract_table_from_html(soup, table_id)
    if not table:
        raise ValueError(f"Table with id '{table_id}' not found in HTML")

    # Extract headers
    thead = table.find("thead")
    header_rows = thead.find_all("tr")
    headers = [th.get_text(strip=True) for th in header_rows[-1].find_all("th")]

    # Extract rows
    tbody = table.find("tbody")
    data_rows = []
    for tr in tbody.find_all("tr"):
        cells = [td.get_text(strip=True) for td in tr.find_all(["th", "td"])]
        if len(cells) == len(headers):
            data_rows.append(cells)
        else:
            print(f"⚠️ Skipping row with {len(cells)} columns (expected {len(headers)})")

    return pd.DataFrame(data_rows, columns=headers)

def scrape_main_and_goalkeeping_tables(html_file_name: str):
    """Scrape both main and goalkeeping tables from single HTML file"""
    main_df = scrape_table_by_id(html_file_name, "results2024-202591_overall")
    gk_df = scrape_table_by_id(html_file_name, "stats_squads_keeper_for")
    return main_df, gk_df

def scrape_final_table(html_file_name: str) -> pd.DataFrame:
    """Scrape only the main table"""
    main_df, _ = scrape_main_and_goalkeeping_tables(html_file_name)
    return main_df

def scrape_keeper_table(html_file_name: str) -> pd.DataFrame:
    """Scrape only the goalkeeping table"""
    _, gk_df = scrape_main_and_goalkeeping_tables(html_file_name)
    return gk_df

if __name__ == "__main__":
    try:
        # Test with your HTML file
        main_df, gk_df = scrape_main_and_goalkeeping_tables("premier_league_stats.html")
        print("Main Table:")
        print(main_df.head())
        print("\nGoalkeeping Table:")
        print(gk_df.head())
    except Exception as e:
        print(f"Error: {e}")