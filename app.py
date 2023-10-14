from flask import Flask, send_file, request, jsonify
import pandas as pd
from io import StringIO
from datetime import datetime

app = Flask(__name__)

@app.route('/rk_summary', methods=['POST'])
def rk_summary():
    # Retrieve JSON data from the incoming request
data = request.get_json()
    print("===== DEBUGGING START =====")
    print("Received JSON Payload: ", data)
    print("Type of Received JSON Payload: ", type(data))
    print("===== DEBUGGING END =====")

    if not data or 'data' not in data:
        return jsonify({"error": "Missing data in request"}), 400

    # Convert received data to DataFrame
    df = pd.DataFrame(data['data'])
    app.logger.info("Successfully read the CSV into a DataFrame.")
        
    # Tony's DataFrame processing logic
    df['Gain/Loss'] = df['Gain/Loss'].str.replace('[$,()]', '', regex=True).astype(float)
    summary_df = df.groupby('Source Number')['Gain/Loss'].sum().reset_index()
    summary_df.columns = ['Source Number', 'Total Gain/Loss']
    summary_df['Total Gain/Loss'] = summary_df['Total Gain/Loss'].round(2)
    app.logger.info("Successfully summarized the DataFrame.")

    csv_file_path = convert_data_to_csv(response_data['final_report'])
    return send_file(csv_file_path, mimetype='text/csv').strftime('%Y%m%d%H%M%S') + '.csv',
            mimetype='text/csv'
        )

if __name__ == '__main__':
    app.run()

def handle_eligibility_status_report():
    body = request.get_json()
    print(body)
    response_data = json.loads(body['eligibility_status_report'])
    csv_file_path = convert_data_to_csv(response_data['eligibility_status_report'])
    return send_file(csv_file_path, mimetype='text/csv')

@app.route('/hce_nhce_status_report', methods=['POST'])


# Cloned route from raj code.py
No Flask route found in raj code.py
