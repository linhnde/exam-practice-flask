import pandas as pd


def compose_data(exam_name):
    data_file = f"{exam_name}_bank.csv"
    data_path = f"data/{data_file}"
    question_data = pd.read_csv(data_path)
    # Complete data, shuffle rows, reset index
    question_data = question_data.sample(frac=1).reset_index(drop=True)
    return question_data


# Pick multiple answers only
# mask = question_bank['correct_1'] == question_bank['correct_1']
# question_bank = question_bank[mask]
