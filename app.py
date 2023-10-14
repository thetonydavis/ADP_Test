
# Complete Flask app code including all necessary imports and both routes
from flask import Flask, request, jsonify, send_file
import csv
from io import StringIO
from werkzeug.utils import secure_filename
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

# Function to clean and convert Gain/Loss column to float
def clean_gain_loss(value):
    try:
        value = value.replace("(", "-").replace(")", "").replace("$", "").replace(",", "").strip()
        return float(value)
    except ValueError:
        return 0.0

@app.route('/webhook', methods=['POST'])
def webhook():
    # Your existing '/webhook' route code here
    # For demonstration purposes, let's assume it returns a simple JSON response.
    return jsonify({'status': 'Webhook route'}), 200

@app.route('/rk_summary', methods=['POST'])
def rk_summary():
    # Obtain file from the incoming request
    file = request.files['rk_file']
    secure_file = secure_filename(file.filename)

    # Initialize dictionaries to store information
    ssn_gain_loss = {}
    ssn_first_name = {}
    ssn_last_name = {}

    # Read the CSV data from the uploaded file
    csv_data = StringIO(file.read().decode())
    reader = csv.DictReader(csv_data)

    # Read and aggregate the Gain/Loss field by Social Security Number
    for row in reader:
        ssn = row['Social Security Number']
        gain_loss = clean_gain_loss(row['Gain_Loss'])
        first_name = row['First Name']
        last_name = row['Last Name']

        if ssn in ssn_gain_loss:
            ssn_gain_loss[ssn] += gain_loss
        else:
            ssn_gain_loss[ssn] = gain_loss
            ssn_first_name[ssn] = first_name
            ssn_last_name[ssn] = last_name

    # Reinitialize the StringIO object for output
    output = StringIO()
    fieldnames = ['Social Security Number', 'First Name', 'Last Name', 'Gain_Loss']
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()

    # Write the aggregated data to the StringIO object
    for ssn, gain_loss in ssn_gain_loss.items():
        writer.writerow({
            'Social Security Number': ssn,
            'First Name': ssn_first_name[ssn],
            'Last Name': ssn_last_name[ssn],
            'Gain_Loss': gain_loss
        })

    # Get the CSV content as a string
    output_str = output.getvalue()

    # Convert the output string to bytes
    output_bytes = StringIO(output_str)

    return send_file(output_bytes,
                     as_attachment=True,
                     attachment_filename='aggregated_gain_loss.csv',
                     mimetype='text/csv')

if __name__ == '__main__':
    app.run(debug=True)
