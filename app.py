from flask import Flask, request, jsonify, send_file
import pandas as pd
import csv
from io import StringIO
import requests
from io import BytesIO

app = Flask(__name__)

def clean_gain_loss(value):
    try:
        value = value.replace("(", "-").replace(")", "").replace("$", "").replace(",", "").strip()
        return float(value)
    except ValueError:
        return 0.0

@app.route('/rk_summary', methods=['POST'])
def rk_summary():
    file_url = request.json.get('file_url')
    
    response = requests.get(file_url)
    if response.status_code != 200:
        return jsonify({"error": "Failed to download the file"}), 500

    file_content = response.text

    csv_file = StringIO(file_content)
    reader = csv.DictReader(csv_file)

    ssn_gain_loss = {}
    ssn_first_name = {}
    ssn_last_name = {}

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
    fieldnames = ['Social Security Number', 'First Name', 'Last Name', 'Gain/Loss']
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()

    for ssn, gain_loss in ssn_gain_loss.items():
        writer.writerow({
            'Social Security Number': ssn,
            'First Name': ssn_first_name[ssn],
            'Last Name': ssn_last_name[ssn],
            'Gain/Loss': gain_loss
        })

    output.seek(0)
output_bytes = BytesIO(output.getvalue().encode())

return send_file(
    output_bytes,
    as_attachment=True,
    attachment_filename='aggregated_gain_loss.csv',
    mimetype='text/csv'
)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
