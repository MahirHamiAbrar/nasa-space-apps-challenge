# exoplanet_candidates.py
"""
Download CANDIDATE exoplanets from NASA Exoplanet Archive using TAP service.
"""
import requests
import os
import csv
import urllib.parse
from io import StringIO

def get_available_tables():
    """
    Fetches and returns the list of all available tables from the NASA Exoplanet Archive TAP service.
    """
    base_url = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync?query="
    query = "select table_name from TAP_SCHEMA.tables"
    
    # Construct URL
    url = base_url + query.replace(' ', '+') + "&format=csv"
    
    response = requests.get(url, timeout=90)
    if response.status_code != 200:
        raise ValueError(f"Failed to fetch table list: {response.status_code}")
    
    # Parse CSV response
    lines = response.text.strip().split('\n')
    tables = [line.strip() for line in lines[1:] if line.strip()]
    
    return tables

def construct_tap_url(table, columns='*', where_clause='', order_by='', limit=None):
    """
    Constructs the TAP query URL for downloading data.
    
    Args:
    - table (str): The table name, e.g., 'cumulative', 'ps', 'toi'.
    - columns (str): Comma-separated columns or '*' for all columns.
    - where_clause (str): WHERE clause conditions (without 'WHERE' keyword).
    - order_by (str): ORDER BY column name.
    - limit (int, optional): Number of rows to limit.
    
    Returns:
    - str: The complete TAP URL.
    """
    base_url = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync?query="
    
    # Build query parts
    query_parts = []
    query_parts.append(f"select {columns}")
    query_parts.append(f"from {table}")
    
    if where_clause:
        query_parts.append(f"where {where_clause}")
    
    if order_by:
        query_parts.append(f"order by {order_by}")
    
    if limit:
        query_parts.append(f"limit {limit}")
    
    # Join with spaces and replace spaces with +
    query = " ".join(query_parts)
    url = base_url + query.replace(' ', '+') + "&format=csv"
    
    return url

def download_data(table, folder='data', columns='*', where_clause='', order_by='', filename=None):
    """
    Downloads data from specified table and saves to CSV.
    
    Args:
    - table (str): Table to query.
    - folder (str): Folder to save the CSV.
    - columns (str): Columns to select.
    - where_clause (str): WHERE clause for filtering.
    - order_by (str): Column to order by.
    - filename (str): Output filename (optional).
    
    Returns:
    - str: Path to saved file.
    """
    print(f"\n{'='*60}")
    print(f"Downloading from table: {table}")
    print(f"Filter: {where_clause if where_clause else 'None (all data)'}")
    print(f"{'='*60}")
    
    # Construct URL
    url = construct_tap_url(table, columns, where_clause, order_by)
    print(f"Query URL: {url[:100]}...")
    
    # Make request
    print("Sending request...")
    response = requests.get(url, timeout=120)
    
    if response.status_code != 200:
        raise ValueError(f"Failed to download data: {response.status_code}\n{response.text}")
    
    # Check if we got data
    if not response.text.strip():
        print("WARNING: Empty response received!")
        return None
    
    # Count rows
    lines = response.text.strip().split('\n')
    data_rows = len(lines) - 1  # Minus header
    print(f"Received {data_rows} rows of data")
    
    if data_rows == 0:
        print("WARNING: No data rows found!")
        return None
    
    # Save to file
    os.makedirs(folder, exist_ok=True)
    if filename is None:
        filename = f"{table}_candidates.csv"
    filepath = os.path.join(folder, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(response.text)
    
    print(f"✓ Data saved to: {filepath}")
    print(f"✓ Total rows: {data_rows}")
    
    return filepath

def download_kepler_candidates(folder='data'):
    """
    Downloads Kepler Object of Interest (KOI) CANDIDATES from the cumulative table.
    """
    return download_data(
        table='cumulative',
        folder=folder,
        where_clause="koi_disposition='CANDIDATE'",
        order_by='kepoi_name',
        filename='kepler_candidates.csv'
    )

def download_tess_candidates(folder='data'):
    """
    Downloads TESS Objects of Interest (TOI) CANDIDATES.
    """
    return download_data(
        table='toi',
        folder=folder,
        where_clause="tfopwg_disp='CP'",  # CP = Community Planet candidate
        order_by='toi',
        filename='tess_candidates.csv'
    )

def download_k2_candidates(folder='data'):
    """
    Downloads K2 planet CANDIDATES.
    """
    return download_data(
        table='k2pandc',
        folder=folder,
        where_clause="k2c_disp='CANDIDATE'",
        order_by='epic_name',
        filename='k2_candidates.csv'
    )


def run_main():
    print("\n" + "="*60)
    print("NASA EXOPLANET ARCHIVE - CANDIDATE DOWNLOADER")
    print("="*60)
    
    # 1. Get available tables
    print("\n[1/4] Fetching available tables...")
    try:
        tables = get_available_tables()
        print(f"✓ Found {len(tables)} tables")
        print("\nAvailable tables:")
        for table in sorted(tables):
            print(f"  • {table}")
    except Exception as e:
        print(f"✗ Error getting tables: {e}")
        tables = []
    
    # 2. Download Kepler candidates
    print("\n[2/4] Downloading Kepler CANDIDATES...")
    try:
        filepath = download_kepler_candidates()
        if filepath:
            print(f"✓ Success!")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # 3. Download TESS candidates
    print("\n[3/4] Downloading TESS CANDIDATES...")
    try:
        filepath = download_tess_candidates()
        if filepath:
            print(f"✓ Success!")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # 4. Download K2 candidates
    print("\n[4/4] Downloading K2 CANDIDATES...")
    try:
        filepath = download_k2_candidates()
        if filepath:
            print(f"✓ Success!")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\n" + "="*60)
    print("DOWNLOAD COMPLETE!")
    print("Check the 'data' folder for your CSV files.")
    print("="*60 + "\n")

if __name__ == '__main__':
    run_main()
