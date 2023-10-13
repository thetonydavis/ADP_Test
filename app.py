from flask import Flask, request, jsonify
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import os

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
    else:
        return jsonify({"error": "'Age' column not found in data"}), 400

    # Authenticate with the Google Sheets API
    credentials_json = json.loads(os.environ['GOOGLE_CREDENTIALS'])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_json)
    client = gspread.authorize(creds)

    # Open the Google Sheet and get the first worksheet
    sheet = client.open("ADP Test Sheet").sheet1

    # Update the Google Sheet with the modified data
    # This is a simplified example and may need to be adjusted based on your specific requirements
    for index, row in df.iterrows():
        sheet.update('A{}:B{}'.format(index+2, index+2), [[row['Age'], row['NewAge']]])

    # Convert the modified DataFrame back to JSON
    result = df.to_json(orient='split')

    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

