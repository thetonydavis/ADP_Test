from flask import Flask, request, jsonify, send_file
import pandas as pd
import gspread
import json
import os
from oauth2client.service_account import ServiceAccountCredentials
import logging
import csv
from io import StringIO

# Setup logging
logging.basicConfig(level=logging.INFO)

# Initialize the Flask application
app = Flask(__name__)

# Function to clean and convert Gain/Loss column to float
def clean_gain_loss(value):
    try:
        value = value.replace("(", "-").replace(")", "").replace("$", "").replace(",", "").strip()
        return float(value)
    except ValueError:
        return 0.0

@app.route('/webhook', methods=['POST'])
def process_data():
    data = request.json  # Assuming data is received as JSON
    try:
        incoming_df = pd.DataFrame(data)
    except ValueError:
        index = range(len(data)) if data else None
        incoming_df = pd.DataFrame(data, index=index)
    
    if 'Age' in incoming_df.columns:
        # Convert 'Age' to integers and then perform the multiplication
        incoming_df['Age'] = incoming_df['Age'].astype(int)
        incoming_df['NewAge'] = incoming_df['Age'] * 2
    
        # ... (the rest of your existing '/webhook' code for interacting with Google Sheets)
    
    return jsonify({"message": "Webhook processed"})

@app.route('/rk_summary', methods=['POST'])
def rk_summary():
    file = request.files['rk_file']
    file_content = file.read().decode()

    # Initialize dictionaries to store information
    ssn_gain_loss = {}
    ssn_first_name = {}
    ssn_last_name = {}

    csv_file = StringIO(file_content)
    reader = csv.DictReader(csv_file)

    for row in reader:
        ssn = row['Social Security Number']
        gain_loss = clean_gain_loss(row['Gain/Loss'])
        first_name = row['First Name']
        last_name = row['Last Name']

        if ssn in ssn_gain_loss:
            ssn_gain_loss[ssn] += gain_loss
        else:
            ssn_gain_loss[ssn] = gain_loss
            ssn_first_name[ssn] = first_name
            ssn_last_name[ssn] = last_name

    output = StringIO()
    fieldnames = ['Social Security Number', 'First Name', 'Last Name', 'Total Gain/Loss']
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()

    for ssn, gain_loss in ssn_gain_loss.items():
        writer.writerow({
            'Social Security Number': ssn,
            'First Name': ssn_first_name[ssn],
            'Last Name': ssn_last_name[ssn],
            'Total Gain/Loss': gain_loss
        })

    output.seek(0)
    return send_file(output, as_attachment=True, attachment_filename='aggregated_gain_loss.csv', mimetype='text/csv')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
