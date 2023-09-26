from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json  # Assuming the incoming request has JSON payload
    print("Received data:", data)  # Print the data to the console

    # Your existing code to create DataFrame and other operations
    df = pd.DataFrame(data)
    # ... rest of your code

    return jsonify({'average_age': average_age})

if __name__ == '__main__':
    app.run(port=5000)


