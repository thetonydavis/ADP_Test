from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    # Get JSON data from the incoming request
    data = request.json
    df = pd.DataFrame([data])
    
    # Perform a basic operation using Pandas
    average_age = df['Age'].astype(int).mean()
    
    # Return the result
    return jsonify({'average_age': average_age})

if __name__ == '__main__':
    app.run(port=5000)

