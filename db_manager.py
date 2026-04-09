import sqlite3
import json
import pandas as pd

DB_FILE = 'threat_data.db'

def init_db():
    """
    Connects to the SQLite database and creates the daily_reports table
    if it doesn't already exist.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_reports (
            id INTEGER PRIMARY KEY,
            run_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            top_threats TEXT,
            cves TEXT,
            targeted_sectors TEXT,
            attack_vectors TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_report(report_dict):
    """
    Receives a Python dictionary, converts lists to JSON strings,
    and inserts a new row into the daily_reports table.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Convert lists to JSON strings
    top_threats = json.dumps(report_dict.get('top_threats', []))
    cves = json.dumps(report_dict.get('cves', []))
    targeted_sectors = json.dumps(report_dict.get('targeted_sectors', []))
    attack_vectors = json.dumps(report_dict.get('attack_vectors', []))
    
    cursor.execute('''
        INSERT INTO daily_reports (top_threats, cves, targeted_sectors, attack_vectors)
        VALUES (?, ?, ?, ?)
    ''', (top_threats, cves, targeted_sectors, attack_vectors))
    
    conn.commit()
    conn.close()

def get_historical_sectors():
    """
    Selects all 'targeted_sectors' from the history, parses the JSON back to a list,
    and returns a Pandas DataFrame with the total count of each sector.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT targeted_sectors FROM daily_reports')
    rows = cursor.fetchall()
    conn.close()
    
    all_sectors = []
    for row in rows:
        if row[0]:
            try:
                # Parse JSON string back to a Python list
                sectors = json.loads(row[0])
                if isinstance(sectors, list):
                    all_sectors.extend(sectors)
            except json.JSONDecodeError:
                pass
                
    # Return count of each sector using Pandas, or an empty DataFrame if no data
    if all_sectors:
        df = pd.DataFrame(all_sectors, columns=['sector'])
        sector_counts = df['sector'].value_counts().reset_index()
        sector_counts.columns = ['Sector', 'Count']
        return sector_counts
    else:
        return pd.DataFrame(columns=['Sector', 'Count'])
