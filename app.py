from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return "Hello, World!"

@app.route('/webhook', methods=['POST'])
def process_data():
    data = request.json  # Assuming data is received as JSON
    try:
        df = pd.DataFrame(data)
    except ValueError:
        # Create an index if data consists of scalar values
        index = range(len(data)) if data else None
        df = pd.DataFrame(data, index=index)

    # Check if 'Age' column exists
    if 'Age' in df.columns:
        # Perform a simple Pandas operation
        df['NewAge'] = df['Age'] * 2
    else:
        return jsonify({"error": "'Age' column not found in data"}), 400

    # Convert the modified DataFrame back to JSON
    result = df.to_json(orient='split')

    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
