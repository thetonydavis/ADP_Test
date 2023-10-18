from flask import Flask, request, jsonify, send_file
import pandas as pd
import requests  # Needed for downloading the CSV file
import io  # Needed for reading the CSV content

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
        
        # Read the CSV content into a DataFrame
        df = pd.read_csv(io.StringIO(response.text))
        
        app.logger.info(f"Successfully read the CSV into a DataFrame: {df.head()}")
        
        # Remove the dollar sign, commas, and parentheses from the 'Gain/Loss' column and convert it to float
        df['Gain/Loss'] = df['Gain/Loss'].str.replace('[$,]', '', regex=True)
        df['Gain/Loss'] = df['Gain/Loss'].apply(lambda x: float(x.replace('(', '-').replace(')', '')) if isinstance(x, str) else x)
        
        # Group by 'Social Security Number' and sum the 'Gain/Loss' column
        summary_df = df.groupby('Social Security Number')['Gain/Loss'].sum().reset_index()
        summary_df.columns = ['Social Security Number', 'Total Gain/Loss']
        
        # Round the 'Total Gain/Loss' column to 2 decimal places
        summary_df['Total Gain/Loss'] = summary_df['Total Gain/Loss'].round(2)

        # Format 'Total Gain/Loss' as currency
        summary_df['Total Gain/Loss'] = summary_df['Total Gain/Loss'].map('${:,.2f}'.format)
        
        app.logger.info(f"Successfully summarized the DataFrame: {summary_df.head()}")
        
        # Write DataFrame to a CSV file
        csv_file_path = "temporary_summary.csv"  # This will save in the current working directory
        summary_df.to_csv(csv_file_path, index=False, encoding='utf-8')
        
        app.logger.info(f"Successfully wrote the DataFrame to a CSV file at {csv_file_path}")

        # Convert the DataFrame to a CSV string
        csv_string = summary_df.to_csv(index=False, encoding='utf-8')
        
        # Send the file
        return jsonify({"csv_data": csv_string})
    
    except Exception as e:
        app.logger.error(f"An error occurred: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/fund_summary', methods=['POST'])
def fund_summary():
    try:
        data = request.json
        if 'file_url' not in data or not data['file_url']:
            return jsonify({"error": "Missing or empty 'file_url' in request data"}), 400

        # Logic to download the CSV file from the 'file_url'
        file_response = requests.get(data['file_url'])
        csv_df = pd.read_csv(io.StringIO(file_response.text))
        
        # Sort the DataFrame by 'Fund Ticker'
        sorted_df = csv_df.sort_values(by=['Fund Ticker'])
        
        # Compute the subtotals for 'Ending Balance' grouped by 'Fund Ticker'
        sorted_df['Ending Balance'] = sorted_df['Ending Balance'].str.replace(',', '').str.replace('$', '').astype(float)
        subtotals = sorted_df.groupby(['Fund Ticker', 'Fund Name'])['Ending Balance'].sum().reset_index()  # Include 'Fund Name' here
        
        # Format 'Ending Balance' as currency with 2 decimals
        subtotals['Ending Balance'] = subtotals['Ending Balance'].apply(lambda x: f"${x:,.2f}")
        
        # Convert the subtotals DataFrame to a dictionary for JSON response
        subtotals_dict = subtotals.to_dict(orient='records')
        
        return jsonify({"fund_summary": subtotals_dict}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/calculate_correlative_destribution', methods=['POST'])
def handle_calculate_correlative_destribution():
    body = request.get_json()
    correlative_destribution = handle_ccd(body)
    csv_file_path = convert_data_to_csv(correlative_destribution)
    return send_file(csv_file_path, mimetype='text/csv')

# Helper function: handle_ccd
def handle_ccd(body: dict) -> dict:
    allowd_hce_limit = remove_percentage_get_float(body['Allowed_HCE_Limit'])
    average_hce = remove_percentage_get_float(body['Avg_HCE'])
    max_allowed_compensation = int(body['Max_Allowed_Comp'])
    employee_data_csv = text_to_csv(body['employee_data_csv'])
    employee_data_csv['Plan_Year_Total_Compensation'] = employee_data_csv['Plan_Year_Total_Compensation'].apply(
        remove_commas_get_int)
    excess_deferral_percentage = average_hce - allowd_hce_limit
    employee_data_csv['Excess_Percentage'] = round(
        excess_deferral_percentage, 2)
    employee_data_csv['Excess_Contribution'] = 0.0
    needed_columns = ['First_Name', 'Last_Name', 'HCE_NHCE',
                      'Plan_Year_Total_Compensation', 'Excess_Percentage', 'Excess_Contribution']
    correlative_destribution = []
    for i, row in employee_data_csv.iterrows():
        if row['HCE_NHCE'] == 'HCE':
            if row['Plan_Year_Total_Compensation'] >= max_allowed_compensation:
                row['Plan_Year_Total_Compensation'] = max_allowed_compensation
            row['Excess_Contribution'] = int((row['Plan_Year_Total_Compensation'] * row['Excess_Percentage']) / 100)
        row['Plan_Year_Total_Compensation'] = '{:,}'.format(row['Plan_Year_Total_Compensation'])
        row['Excess_Contribution'] = '{:,}'.format(row['Excess_Contribution'])
        new_row = row[needed_columns]
        correlative_destribution.append(new_row.to_dict())
    return correlative_destribution

# Helper function: convert_data_to_csv
def convert_data_to_csv(data: dict) -> str:
    csv_data = pd.DataFrame.from_dict(data)
    csv_data.to_csv(config.CSV_FILE_PATH, index=False)
    return config.CSV_FILE_PATH
