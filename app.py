from flask import Flask, request, jsonify
import pandas as pd
import gspread
import json
import os
from oauth2client.service_account import ServiceAccountCredentials
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def process_data():
    data = request.json  # Assuming data is received as JSON
    try:
        incoming_df = pd.DataFrame(data)
    except ValueError:
        index = range(len(data)) if data else None
        incoming_df = pd.DataFrame(data, index=index)

    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials_json = os.environ['GOOGLE_CREDENTIALS_JSON']
    credentials_info = json.loads(credentials_json)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_info, scope)

    client = gspread.authorize(creds)
    sheet = client.open("ADP Test Sheet").sheet1

    # Fetch all records from the Google Sheet
    records = sheet.get_all_records()
    df = pd.DataFrame.from_records(records)

    if 'Age' in incoming_df.columns:
        # Convert 'Age' to integers and then perform the multiplication
        incoming_df['Age'] = incoming_df['Age'].astype(int)
        incoming_df['NewAge'] = incoming_df['Age'] * 2

        # Find the next row index to update in Google Sheet
        new_row_index = len(df) + 1  # +1 to account for header

        try:
            # Convert to Python native int
            new_age_value = int(incoming_df['NewAge'].iloc[-1])
            # Update the Google Sheet
            sheet.update_cell(new_row_index, 3, new_age_value)
            logging.info('Google Sheet updated successfully')
        except gspread.exceptions.APIError as e:
            logging.error(f"Failed to update Google Sheet: {e}")
            return jsonify({"error": "Failed to update Google Sheet"}), 500
    else:
        error_message = "'Age' column not found in data"
        logging.error(error_message)
        return jsonify({"error": error_message}), 400

    # Convert the modified DataFrame back to JSON
    result = incoming_df.to_json(orient='split')
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
