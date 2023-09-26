from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    # Create a sample DataFrame
    df = pd.DataFrame({
        'Name': ['Alice', 'Bob', 'Charlie'],
        'Age': [25, 30, 35]
    })

    # Perform a basic operation using Pandas
    average_age = df['Age'].mean()

    # Return the result
    return jsonify({'average_age': average_age})

if __name__ == '__main__':
    app.run(port=5000)
