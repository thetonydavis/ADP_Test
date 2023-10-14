from flask import Flask, send_file, request, jsonify
import pandas as pd
from datetime import datetime
from io import StringIO
import os

app = Flask(__name__)

@app.route('/rk_summary', methods=['POST'])
def rk_summary():
    data = request.get_json()
    
    print("===== DEBUGGING START =====")
    print("Received JSON Payload: ", data)
    print("Type of Received JSON Payload: ", type(data))
    print("===== DEBUGGING END =====")
    
    expected_keys = ['file_url', 'Max_Allowed_Com', 'Avg_HCE', 'Avg_NHCE', 'Allowed_HCE_Limit', 'employee_data_csv', 'HCE_Status']
    if not all(key in data for key in expected_keys):
        return jsonify({"error": "Missing one or more required keys in request"}), 400

    # Assuming 'employee_data_csv' contains CSV data as a string
    csv_data = data.get('employee_data_csv', "")
    df = pd.read_csv(StringIO(csv_data))

    # User's existing DataFrame processing logic
    df['Gain/Loss'] = df['Gain/Loss'].str.replace('[$,()]', '', regex=True).astype(float)
    summary_df = df.groupby('Source Number')['Gain/Loss'].sum().reset_index()
    summary_df.columns = ['Source Number', 'Total Gain/Loss']
    summary_df['Total Gain/Loss'] = summary_df['Total Gain/Loss'].round(2)

    # Save the DataFrame to a CSV file
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    csv_file_path = f"generated_summary_{timestamp}.csv"
    summary_df.to_csv(csv_file_path, index=False)

    return send_file(csv_file_path, mimetype='text/csv', as_attachment=True, download_name=csv_file_path)

if __name__ == '__main__':
    app.run()
