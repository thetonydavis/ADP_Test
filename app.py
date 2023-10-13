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
        df = pd.DataFrame(data)
    except ValueError:
        # Create an index if data consists of scalar values
        index = range(len(data)) if data else None
        df = pd.DataFrame(data, index=index)

    # Check if 'Age' column exists
    if 'Age' in df.columns:
        # Perform a simple Pandas operation
        df['NewAge'] = df['Age'] * 2

        # Accessing Google Sheets
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

        # Load credentials from environment variable
        credentials_json = os.environ['GOOGLE_CREDENTIALS_JSON']
        credentials_info = json.loads(credentials_json)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_info, scope)

        client = gspread.authorize(creds)
        sheet = client.open("ADP Test Sheet").sheet1

        try:
            # Assuming each webhook call corresponds to a single new row being added
            # Finding the row index for the new data
            new_row_index = len(sheet.get_all_records()) + 2  # +1 to account for header, +1 for new row

            # Updating the 'NewAge' column for the new row
            new_age_value = df['NewAge'].iloc[-1]  # Getting the last 'NewAge' value from df
            sheet.update_cell(new_row_index, 3, new_age_value)  # 'NewAge' is the 3rd column

            logging.info('Google Sheet updated successfully')

        except gspread.exceptions.APIError as e:
            logging.error(f"Failed to update Google Sheet: {e}")
            return jsonify({"error": "Failed to update Google Sheet"}), 500

    else:
        error_message = "'Age' column not found in data"
        logging.error(error_message)
        return jsonify({"error": error_message}), 400

    # Convert the modified DataFrame back to JSON
    result = df.to_json(orient='split')

    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
