import os
import pandas as pd


def compose_data(exam_name):
    bucket_name = "exam-banks"
    file_name = f"{exam_name}_bank.csv"
    file_path = f"gs://{bucket_name}/{file_name}"
    question_data = pd.read_csv(file_path)
    # Complete data, shuffle rows, reset index
    # question_data = question_data.sample(frac=1).reset_index(drop=True)
    # Pick multiple answers only
    # mask = question_data['correct_1'] == question_data['correct_1']
    # question_data = question_data[mask]
    return question_data
