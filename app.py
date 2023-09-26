from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print("Received data:", data)
    
    df = pd.DataFrame([data])
    
    # Perform your operations here
    # For example, calculating the average age if the 'Age' column exists
    if 'COL$C' in df.columns:
        average_age = df['COL$C'].astype(int).mean()
        return jsonify({'average_age': average_age})
    else:
        return jsonify({'message': 'Age column not found'})

if __name__ == '__main__':
    app.run(port=5000)


