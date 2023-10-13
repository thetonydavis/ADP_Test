from flask import Flask, request, jsonify
import pandas as pd
import gspread
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
        creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
        client = gspread.authorize(creds)
        sheet = client.open("ADP Test Sheet").sheet1
        
        # Assuming NewAge is the 5th column (index 4) and update starts from the 2nd row
        new_age_col_index = 4
        row_start = 2
        
        # Updating Google Sheets with NewAge values
        for i, new_age_value in enumerate(df['NewAge'], start=row_start):
            sheet.update_cell(i, new_age_col_index, new_age_value)
        
        logging.info('Google Sheet updated successfully')
    else:
        error_message = "'Age' column not found in data"
        logging.error(error_message)
        return jsonify({"error": error_message}), 400
    
    # Convert the modified DataFrame back to JSON
    result = df.to_json(orient='split')
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

