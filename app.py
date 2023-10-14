from flask import Flask, request, jsonify, send_file
import pandas as pd
import requests
import io
import logging

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
        
        summary_df = df.describe()
        
        app.logger.info("Successfully summarized the DataFrame.")
        
        output = io.StringIO()
        summary_df.to_csv(output, index=False)
        
        output.seek(0)
        return send_file(output, as_attachment=True, attachment_filename='summary.csv', mimetype='text/csv')
    
    except Exception as e:
        app.logger.error(f"An error occurred: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
