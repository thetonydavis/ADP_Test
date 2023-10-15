
from flask import Flask, request, jsonify, send_file
import pandas as pd
import requests
import io
import logging
import os

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
        
        app.logger.info(f"Successfully read the CSV into a DataFrame: {df.head()}")
        
        # Remove the dollar sign, commas, and parentheses from the 'Gain/Loss' column and convert it to float
        df['Gain/Loss'] = df['Gain/Loss'].str.replace('[$,]', '', regex=True)
        df['Gain/Loss'] = df['Gain/Loss'].apply(lambda x: float(x.replace('(', '-').replace(')', '')) if isinstance(x, str) else x)
        
        # Group by 'Social Security Number' and sum the 'Gain/Loss' column
        summary_df = df.groupby('Social Security Number')['Gain/Loss'].sum().reset_index()
        summary_df.columns = ['Social Security Number', 'Total Gain/Loss']
        
        # Round the 'Total Gain/Loss' column to 2 decimal places
        summary_df['Total Gain/Loss'] = summary_df['Total Gain/Loss'].round(2)

        # Format 'Total Gain/Loss' as currency
        summary_df['Total Gain/Loss'] = summary_df['Total Gain/Loss'].map('${:,.2f}'.format)
        
        app.logger.info(f"Successfully summarized the DataFrame: {summary_df.head()}")
        
        # Write DataFrame to a CSV file
        csv_file_path = "temporary_summary.csv"  # This will save in the current working directory
        summary_df.to_csv(csv_file_path, index=False, encoding='utf-8')
        
        app.logger.info(f"Successfully wrote the DataFrame to a CSV file at {csv_file_path}")
        
        # Send the file
        return send_file(csv_file_path, mimetype='text/csv', as_attachment=True)
    
    except Exception as e:
        app.logger.error(f"An error occurred: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
