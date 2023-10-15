from flask import Flask, request, jsonify, send_file
import pandas as pd
import requests
import io
import logging
import os
import uuid  # Import uuid to generate unique file names

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

@app.route('/rk_summary', methods=['POST'])
def rk_summary():
    try:
        data = request.json
        app.logger.info(f"Received data: {data}")

        if 'file_url' not in data or not data['file_url']:
            return jsonify({"error": "Missing or empty 'file_url' in request data"}), 400

        file_url = data['file_url']
        
        app.logger.info(f"Received file_url: {file_url}")
        
        response = requests.get(file_url)
        response.raise_for_status()
        
        app.logger.info("Successfully downloaded the file.")
        
        # Read the CSV content into a DataFrame
        df = pd.read_csv(io.StringIO(response.text))
        
        app.logger.info("Successfully read the CSV into a DataFrame.")
        
        # Remove the dollar sign and commas from the 'Gain/Loss' column and convert it to float
        df['Gain/Loss'] = df['Gain/Loss'].str.replace('[$,()]', '', regex=True).astype(float)
        
        # Create sub-totals for the 'Gain/Loss' column
        summary_df = df.groupby('Source Number')['Gain/Loss'].sum().reset_index()
        summary_df.columns = ['Source Number', 'Total Gain/Loss']
        
        # Round the 'Total Gain/Loss' column to 2 decimal places
        summary_df['Total Gain/Loss'] = summary_df['Total Gain/Loss'].round(2)
        
        app.logger.info("Successfully summarized the DataFrame.")
        
        # Write DataFrame to a CSV file
        csv_file_path = "temporary_summary.csv"  # This will save in the current working directory
        summary_df.to_csv(csv_file_path, index=False, encoding='utf-8')
        
        # Assuming file_path is the path to the file you want to send
        return send_file(csv_file_path, as_attachment=True, download_name='summary.csv')
    
    except Exception as e:
        app.logger.error(f"An error occurred: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
