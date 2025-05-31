import os
import gspread
import csv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# Google Sheets API scopes
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Load credentials path from environment variable or default
CREDS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "credentials.json")

# Validate credentials file existence
if not os.path.isfile(CREDS_PATH):
    raise FileNotFoundError(f"Google credentials file not found at: {CREDS_PATH}")

# Authenticate and build clients
creds = Credentials.from_service_account_file(CREDS_PATH, scopes=SCOPES)
gc = gspread.authorize(creds)
sheets_service = build("sheets", "v4", credentials=creds)

# Spreadsheet ID to update
SPREADSHEET_ID = "YOUR_ID"
spreadsheet = gc.open_by_key(SPREADSHEET_ID)

# Cities and corresponding CSV files
cities = {
    "Poznan": "poznan.csv",
    "Warsaw": "warsaw.csv"
}

def create_or_clear_worksheet(title, rows=100, cols=20):
    """Create worksheet if it doesn't exist, else clear it."""
    try:
        sheet = spreadsheet.worksheet(title)
        sheet.clear()
    except gspread.exceptions.WorksheetNotFound:
        sheet = spreadsheet.add_worksheet(title=title, rows=str(rows), cols=str(cols))
    return sheet

def add_pie_chart(service, spreadsheet_id, source_sheet_id, chart_sheet_id, num_rows):
    """Add a pie chart to a given sheet in the spreadsheet."""
    requests = [
        {
            "addChart": {
                "chart": {
                    "spec": {
                        "title": "Category Distribution",
                        "pieChart": {
                            "legendPosition": "RIGHT_LEGEND",
                            "threeDimensional": False,
                            "domain": {
                                "sourceRange": {
                                    "sources": [{
                                        "sheetId": source_sheet_id,
                                        "startRowIndex": 1,
                                        "endRowIndex": num_rows + 1,
                                        "startColumnIndex": 0,
                                        "endColumnIndex": 1
                                    }]
                                }
                            },
                            "series": {
                                "sourceRange": {
                                    "sources": [{
                                        "sheetId": source_sheet_id,
                                        "startRowIndex": 1,
                                        "endRowIndex": num_rows + 1,
                                        "startColumnIndex": 1,
                                        "endColumnIndex": 2
                                    }]
                                }
                            }
                        }
                    },
                    "position": {
                        "overlayPosition": {
                            "anchorCell": {
                                "sheetId": chart_sheet_id,
                                "rowIndex": 1,
                                "columnIndex": 1
                            },
                            "offsetXPixels": 0,
                            "offsetYPixels": 0,
                            "widthPixels": 2500,
                            "heightPixels": 1000
                        }
                    }
                }
            }
        }
    ]

    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={"requests": requests}
    ).execute()

def main():
    for city, filename in cities.items():
        print(f"Processing data for: {city}")

        # Load CSV data
        try:
            with open(filename, newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                data = list(reader)
        except FileNotFoundError:
            print(f"Error: CSV file not found: {filename}")
            continue

        # Create or clear data sheet and update
        data_sheet = create_or_clear_worksheet(city)
        print(f"Creating data sheet for {city}...")
        data_sheet.update(data, "A1")

        # Count categories from CSV (assuming category in 5th column - index 4)
        category_counts = {}
        for row in data[1:]:  # Skip header
            if len(row) > 4:
                category = row[4]
                category_counts[category] = category_counts.get(category, 0) + 1

        # Prepare category data
        category_data = [["Category", "Count"]] + [[k, v] for k, v in category_counts.items()]

        # Create or clear category sheet and update
        category_sheet_name = f"{city}_Category"
        category_sheet = create_or_clear_worksheet(category_sheet_name, rows=20, cols=2)
        print(f"Creating category sheet for {city}...")
        category_sheet.update(category_data, "A1")

        # Create or clear chart sheet
        chart_sheet_name = f"{city}_Chart"
        chart_sheet = create_or_clear_worksheet(chart_sheet_name, rows=20, cols=10)

        # Refresh sheet ID mapping
        spreadsheet_info = sheets_service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
        sheet_id_map = {s["properties"]["title"]: s["properties"]["sheetId"] for s in spreadsheet_info["sheets"]}

        source_id = sheet_id_map[category_sheet_name]
        chart_sheet_id = sheet_id_map[chart_sheet_name]
        num_rows = len(category_data) - 1  # exclude header

        # Add pie chart
        print(f"Creating chart for {city}...")
        add_pie_chart(sheets_service, SPREADSHEET_ID, source_id, chart_sheet_id, num_rows)

    print("All data and charts successfully uploaded to Google Sheets.")

if __name__ == "__main__":
    main()
