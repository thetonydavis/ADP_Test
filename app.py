
from flask import Flask, request, jsonify, send_file
import pandas as pd
import requests
import io
import logging
import os
from datetime import datetime
from boxsdk import OAuth2, Client

# Initialize the Box SDK
auth = OAuth2(
    client_id='dzp83ne72un5revhj27o272sc471v81i',
    client_secret='u6MZ7XgMPCsKJKMsWgIICwQ9nKTVWAXm',
    access_token='kWiJ155fJ2fShv9SFnqT0q5nceYD8KSv',  # This should be securely stored and refreshed
)
client = Client(auth)

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
        
        df = pd.read_csv(io.StringIO(response.text))
        app.logger.info("Successfully read the CSV into a DataFrame.")
        
        df['Gain/Loss'] = df['Gain/Loss'].str.replace('[$,()]', '', regex=True).astype(float)
        summary_df = df.groupby('Source Number')['Gain/Loss'].sum().reset_index()
        summary_df.columns = ['Source Number', 'Total Gain/Loss']
        summary_df['Total Gain/Loss'] = summary_df['Total Gain/Loss'].round(2)
        
        app.logger.info("Successfully summarized the DataFrame.")
        
        timestamp_str = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_filename = f"summary_{timestamp_str}.csv"

        # Log the unique filename before attempting to upload to Box
        app.logger.info(f"Attempting to upload file with name: {unique_filename}")

        csv_file_path = os.path.join(os.getcwd(), unique_filename)
        summary_df.to_csv(csv_file_path, index=False, encoding='utf-8')
        
        # Upload the file to Box
        folder_id = 'Waivz'
        folder = client.folder(folder_id=folder_id).get()
        with open(csv_file_path, 'rb') as f:
            uploaded_file = folder.upload_stream(f, unique_filename)
        
        return send_file(csv_file_path, mimetype='text/csv', as_attachment=True, attachment_filename=unique_filename)
    
    except Exception as e:
        app.logger.error(f"An error occurred: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
