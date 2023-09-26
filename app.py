from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def process_data():
    # Get JSON data from the incoming request
    data = request.json
    df = pd.DataFrame(data)
    
    # Perform a simple Pandas operation
    # Multiply the 'Age' column by 2 and store it in a new column 'Double_Age'
    df['Double_Age'] = df['Age'] * 2
    
    # Convert the modified DataFrame back to JSON
    result = df.to_json(orient='split')
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(port=5000)

