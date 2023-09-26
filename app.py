from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)

@app.route('/process_data', methods=['POST'])
def process_data():
    # Get JSON data from the incoming request
    data = request.json
    df = pd.DataFrame(data)
    
    # Perform a simple Pandas operation
    df['new_column'] = df['existing_column'] * 2
    
    # Convert the modified DataFrame back to JSON
    result = df.to_json(orient='split')
    
    return jsonify(result)

if __name__ == '__main__':
    app.run()
