
from flask import Flask, request, jsonify
import os
import tempfile
import uuid
import pandas as pd
from typing import List, Dict

app = Flask(__name__)

# Configuration constants
TEXT_FILE_PATH = os.path.join(
    tempfile.gettempdir(),
    f'{uuid.uuid1()}.txt'
)

CSV_FILE_PATH = os.path.join(
    tempfile.gettempdir(),
    f'{uuid.uuid1()}.csv'
)

HCE_AMOUNT = 130000
HCE_OWNERSHIP_PERCENTAGE = 5
HCE_FAMILY_RELATIONSHIP = 'Yes'

DP_MAXIMUM_COMPENSATION = 305000

def remove_percentage_get_float(text: str) -> float:
    text = text.replace('%', '')
    text = float(text)
    return text

def text_to_csv(text: str) -> pd.DataFrame:
    with open(TEXT_FILE_PATH, 'w') as file:
        file.write(text)
    csv_data = pd.read_csv(TEXT_FILE_PATH)
    os.unlink(TEXT_FILE_PATH)
    return csv_data

def handle_ccd(body: dict) -> dict:
    allowd_hce_limit = remove_percentage_get_float(body['Allowed_HCE_Limit'])
    average_hce = remove_percentage_get_float(body['Avg_HCE'])
    max_allowed_compensation = int(body['Max_Allowed_Comp'])
    employee_data_csv = text_to_csv(body['employee_data_csv'])

    excess_deferral_percentage = average_hce - allowd_hce_limit
    employee_data_csv['Excess_Percentage'] = round(
        excess_deferral_percentage, 2)
    employee_data_csv['Excess_Contribution'] = 0.0
    needed_columns = ['First_Name', 'Last_Name', 'HCE_NHCE',
                      'Plan_Year_Total_Compensation', 'Excess_Percentage', 'Excess_Contribution']
    correlative_destribution = []
    for i, row in employee_data_csv.iterrows():
        if row['HCE_NHCE'] == 'HCE':
            if int(row['Plan_Year_Total_Compensation']) >= max_allowed_compensation:
                row['Plan_Year_Total_Compensation'] = max_allowed_compensation
            row['Excess_Contribution'] = int((row['Plan_Year_Total_Compensation'] * row['Excess_Percentage']) / 100)
        new_row = row[needed_columns]
        correlative_destribution.append(new_row.to_dict())
    return correlative_destribution

def convert_data_to_csv(data: dict) -> str:
    csv_data = pd.DataFrame.from_dict(data)
    csv_data.to_csv(CSV_FILE_PATH, index=False)
    return CSV_FILE_PATH

@app.route('/calculate_correlative_destribution', methods=['POST'])
def handle_calculate_correlative_destribution():
    body = request.get_json()
    correlative_destribution = handle_ccd(body)
    csv_file_path = convert_data_to_csv(correlative_destribution)
    return jsonify({'csv_file_path': csv_file_path})

if __name__ == '__main__':
    app.run(debug=True)
