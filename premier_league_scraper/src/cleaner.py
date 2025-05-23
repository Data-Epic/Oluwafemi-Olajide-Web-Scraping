import pandas as pd
from pathlib import Path
from scraper import scrape_final_table, scrape_keeper_table

def clean_premier_league_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans and formats Premier League final table stats.
    """
    # Step 1: Rename ambiguous columns
    df.rename(columns={
        "Squad": "Team",
        "GF": "Goals For",
        "GA": "Goals Against"
    }, inplace=True)

    # Step 2: Clean 'Attendance' column (remove commas)
    if "Attendance" in df.columns:
        df["Attendance"] = df["Attendance"].str.replace(",", "", regex=False)

    # Step 3: Convert numeric columns
    numeric_columns = [
        "MP", "W", "D", "L", "Goals For", "Goals Against", "GD",
        "Pts", "Pts/MP", "xG", "xGA", "xGD", "xGD/90", "Attendance"
    ]
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Step 4: Extract goal count from 'Top Team Scorer' column
    if "Top Team Scorer" in df.columns:
        df["Top Scorer Goals"] = df["Top Team Scorer"].str.extract(r"-(\d+)$").astype(float)
        df["Top Team Scorer"] = df["Top Team Scorer"].str.extract(r"^(.*?)(?:-\d+)?$")[0].str.strip()

    # Step 5: Clean up GD column (remove "+" sign if present)
    if "GD" in df.columns and df["GD"].dtype == object:
        df["GD"] = df["GD"].str.replace("+", "", regex=False)
        df["GD"] = pd.to_numeric(df["GD"], errors="coerce")

    # Step 6: Clean 'Goalkeeper' column
    if "Goalkeeper" in df.columns:
        df["GK Appearances"] = df["Goalkeeper"].str.extract(r"\((\d+)\s+apps\)").astype(float)
        df["Goalkeeper"] = df["Goalkeeper"].str.extract(r"^(.*?)\s+\(\d+\s+apps\)")[0].str.strip()

    # Step 7: Sort by Points descending
    if "Pts" in df.columns:
        df.sort_values("Pts", ascending=False, inplace=True)
        df.reset_index(drop=True, inplace=True)

    # Step 8: Rearranged columns (if all present)
    preferred_order = [
        "Rk", "Team", "MP", "W", "D", "L", "Goals For", "Goals Against", "GD",
        "xG", "xGA", "xGD", "xGD/90",
        "Pts", "Pts/MP", "Top Team Scorer", "Top Scorer Goals",
        "Goalkeeper", "GK Appearances",
        "Attendance", "Last 5", "Notes"
    ]
    df = df[[col for col in preferred_order if col in df.columns]]

    return df

def clean_keeper_stats(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans and renames goalkeeper squad stats DataFrame.
    """
    # Flatten multi-level column headers if needed
    df.columns = [' '.join(col).strip() if isinstance(col, tuple) else col for col in df.columns]

    # Rename key columns
    df = df.rename(columns={"Squad": "Team"})

    # Additional cleaning can go here if needed
    return df

def get_data_path(filename):
    """Helper function to get correct file paths"""
    current_dir = Path(__file__).parent
    return current_dir / filename

if __name__ == "__main__":
    try:
        # Clean league table
        stats_path = get_data_path("premier_league_stats.html")
        raw_df = scrape_final_table(stats_path)
        cleaned_df = clean_premier_league_table(raw_df)
        print("Cleaned League Table:")
        print(cleaned_df.head())

        # Clean goalkeeper table
        raw_gk_df = scrape_keeper_table(stats_path)
        cleaned_gk_df = clean_keeper_stats(raw_gk_df)
        print("\nCleaned Goalkeeper Stats:")
        print(cleaned_gk_df.head())

    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
        print("Please make sure 'premier_league_stats.html' is in the same directory as this script.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")