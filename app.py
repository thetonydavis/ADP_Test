
from flask import Flask, request, jsonify, send_file
import pandas as pd
import requests
import io

app = Flask(__name__)

@app.route('/rk_summary', methods=['POST'])
def rk_summary():
    try:
        data = request.json
        file_url = data['file_url']
        
        response = requests.get(file_url)
        response.raise_for_status()
        
        # Assume the file is a CSV for this example
        df = pd.read_csv(io.StringIO(response.text))
        
        # Your logic here to summarize the DataFrame
        summary_df = df.describe()  # Replace with your actual logic
        
        output = io.StringIO()
        summary_df.to_csv(output, index=False)
        
        output.seek(0)
        return send_file(output, as_attachment=True, attachment_filename='summary.csv', mimetype='text/csv')
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
