from flask import Flask, send_file, request, jsonify
import pandas as pd
from io import StringIO
import json
from datetime import datetime

app = Flask(__name__)

@app.route('/rk_summary', methods=['POST'])
def rk_summary():
    # Retrieve JSON data from the incoming request
    data = request.get_json()
    if not data or 'data' not in data:
        return jsonify({"error": "Missing data in request"}), 400

    # Convert received data to DataFrame
    df = pd.DataFrame(data['data'])

    # Tony's DataFrame processing code
    app.logger.info("Successfully read the CSV into a DataFrame.")
        
        df['Gain/Loss'] = df['Gain/Loss'].str.replace('[$,()]', '', regex=True).astype(float)
        summary_df = df.groupby('Source Number')['Gain/Loss'].sum().reset_index()
        summary_df.columns = ['Source Number', 'Total Gain/Loss']
        summary_df['Total Gain/Loss'] = summary_df['Total Gain/Loss'].round(2)
        
        app.logger.info("Successfully summarized the DataFrame.")
        
        timestamp_str = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_filename = f"summary_{timestamp_str}.csv"

    # Save DataFrame to a CSV file
    csv_buffer = StringIO()
    summary_df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)

    # Use Flask's send_file to return the CSV file
    return send_file(
        csv_buffer,
        as_attachment=True,
        download_name='summary_' + datetime.now().strftime('%Y%m%d%H%M%S') + '.csv',
        mimetype='text/csv'
    )

if __name__ == '__main__':
    app.run()
